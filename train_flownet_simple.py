#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
original author: Linjian Zhang

CUDA_VISIBLE_DEVICES=0,1 python3 train_flownet_simple.py

"""

import tensorflow as tf
import tensorflow.contrib.slim as slim
import random
import os
import cv2
import numpy as np
import shutil
import struct
import time
from matplotlib import pyplot as plt
import pdb


dir0 = '20190710_755_01'
# dir0 = '20190710_333_01'
net_name = 'flownet_simple/'
dir_restore = 'model/flownet_simple/20190703_01/model-5'
dir_data = '/home/ukcheol/dataset/FlyingChairs/data/'

lr_base = 1e-3              # initial learning rate
epoch_lr_decay = 500        # every # epoch, lr will decay 0.1
epoch_max = 20              # max epoch
max_to_keep = 5             # number of model to save
batch_size = 64             # bs
train_pairs_number = 20000  # number of train samples
val_iter = 2                # validation batch
use_gpu_1 = True
W, H = 512, 384
val_pairs_number = batch_size * val_iter
iter_per_epoch = train_pairs_number // batch_size
# epoch_save = epoch_max // max_to_keep
epoch_save = 1
########################################
dir_models = 'model/' + net_name
dir_logs = 'log/' + net_name
dir_model = dir_models + dir0
dir_log_train = dir_logs + dir0 + '_train'
dir_log_test = dir_logs + dir0 + '_test'
if not os.path.exists(dir_models):
    os.mkdir(dir_models)
if not os.path.exists(dir_logs):
    os.mkdir(dir_logs)
if os.path.exists(dir_model):
    shutil.rmtree(dir_model)
if os.path.exists(dir_log_train):
    shutil.rmtree(dir_log_train)
if os.path.exists(dir_log_test):
    shutil.rmtree(dir_log_test)

os.mkdir(dir_model)
os.mkdir(dir_log_train)
os.mkdir(dir_log_test)
########################################


def remove_file(directory_list):
    if '.directory' in directory_list:
        directory_list.remove('.directory')
    return directory_list


def load_data():
    img1_list_t = []
    img2_list_t = []
    flow_list_t = []
    img1_list_v = []
    img2_list_v = []
    flow_list_v = []
    namelist = remove_file(os.listdir(dir_data))
    namelist.sort()
    for i in range(train_pairs_number+val_pairs_number):
        if i < train_pairs_number:
            flow_list_t.append(dir_data + namelist[3*i])
            img1_list_t.append(dir_data + namelist[3*i+1])
            img2_list_t.append(dir_data + namelist[3*i+2])
        else:
            flow_list_v.append(dir_data + namelist[3*i])
            img1_list_v.append(dir_data + namelist[3*i+1])
            img2_list_v.append(dir_data + namelist[3*i+2])

    assert len(img1_list_t) == len(img2_list_t)
    assert len(img1_list_t) == len(flow_list_t)
    assert len(img1_list_v) == len(img2_list_v)
    assert len(img1_list_v) == len(flow_list_v)
    return img1_list_t, img2_list_t, flow_list_t, img1_list_v, img2_list_v, flow_list_v


class Data(object):
    def __init__(self, list1, list2, list3, bs=batch_size, shuffle=True, minus_mean=True):
        self.list1 = list1
        self.list2 = list2
        self.list3 = list3
        self.bs = bs
        self.index = 0
        self.number = len(self.list1)
        self.index_total = list(range(self.number))
        self.shuffle = shuffle
        self.minus_mean = minus_mean
        if self.shuffle: self.index_total = random.sample(self.index_total, len(self.index_total))

    def read_flow(self, name):
        f = open(name, "rb")
        data = f.read()
        f.close()
        width = struct.unpack('@i', data[4:8])[0]
        height = struct.unpack('@i', data[8:12])[0]
        flowdata = np.zeros((height, width, 2))
        for i in range(width*height):
            data_u = struct.unpack('@f', data[12+8*i:16+8*i])[0]
            data_v = struct.unpack('@f', data[16+8*i:20+8*i])[0]
            n = int(i / width)
            k = np.mod(i, width)
            flowdata[n, k, :] = [data_u, data_v]
        return flowdata

    def next_batch(self):
        start = self.index
        self.index += self.bs
        if self.index > self.number:
            if self.shuffle: self.index_total = random.sample(self.index_total, len(self.index_total))
            self.index = 0
            start = self.index
            self.index += self.bs
        end = self.index
        img1_batch = []
        img2_batch = []
        flow_batch = []
        for i in range(start, end):
            img1 = cv2.imread(self.list1[self.index_total[i]]).astype(np.float32)
            img1_batch.append(img1)
            img2 = cv2.imread(self.list2[self.index_total[i]]).astype(np.float32)
            img2_batch.append(img2)
            flow = self.read_flow(self.list3[self.index_total[i]])
            flow_batch.append(flow)

        return np.array(img1_batch), np.array(img2_batch), np.array(flow_batch)


class Net(object):
    def __init__(self, use_gpu_1=True):
        self.x1 = tf.placeholder(tf.float32, [None, H, W, 3], name='x1')  # image1
        self.x2 = tf.placeholder(tf.float32, [None, H, W, 3], name='x2')  # image2
        self.x3 = tf.placeholder(tf.float32, [None, H, W, 2], name='x3')  # label
        self.lr = tf.placeholder(tf.float32, [], name='lr')  # lr
        with tf.variable_scope('conv'):
            # pdb.set_trace()
            concat1 = tf.concat([self.x1, self.x2], 3)

            ### Origianl FlowNet
            conv1 = slim.conv2d(concat1, 64, [7, 7], 2, scope='conv1')
            conv2 = slim.conv2d(conv1, 128, [5, 5], 2, scope='conv2')
            conv3 = slim.conv2d(conv2, 256, [5, 5], 2, scope='conv3')

            ### FlowNet-SD
            # conv1 = slim.conv2d(concat1, 64, [3, 3], 2, scope='conv1')
            # conv2 = slim.conv2d(conv1, 128, [3, 3], 2, scope='conv2')
            # conv3 = slim.conv2d(conv2, 256, [3, 3], 2, scope='conv3')

            conv3_1 = slim.conv2d(conv3, 256, [3, 3], 1, scope='conv3_1')
            conv4 = slim.conv2d(conv3_1, 512, [3, 3], 2, scope='conv4')
            conv4_1 = slim.conv2d(conv4, 512, [3, 3], 1, scope='conv4_1')
            conv5 = slim.conv2d(conv4_1, 512, [3, 3], 2, scope='conv5')
            conv5_1 = slim.conv2d(conv5, 512, [3, 3], 1, scope='conv5_1')
            conv6 = slim.conv2d(conv5_1, 1024, [3, 3], 2, scope='conv6')
            conv6_1 = slim.conv2d(conv6, 1024, [3, 3], 1, scope='conv6_1')
            predict6 = slim.conv2d(conv6_1, 2, [3, 3], 1, activation_fn=None, scope='pred6')

        with tf.variable_scope('deconv'):
            # 12 * 16 flow
            deconv5 = slim.conv2d_transpose(conv6_1, 512, [4, 4], 2, scope='deconv5')
            deconvflow6 = slim.conv2d_transpose(predict6, 2, [4, 4], 2, 'SAME', scope='deconvflow6')
            concat5 = tf.concat([conv5_1, deconv5, deconvflow6], 3, name='concat5')
            predict5 = slim.conv2d(concat5, 2, [3, 3], 1, 'SAME', activation_fn=None, scope='predict5')
            # 24 * 32 flow
            deconv4 = slim.conv2d_transpose(concat5, 256, [4, 4], 2, 'SAME', scope='deconv4')
            deconvflow5 = slim.conv2d_transpose(predict5, 2, [4, 4], 2, 'SAME', scope='deconvflow5')
            concat4 = tf.concat([conv4_1, deconv4, deconvflow5], 3, name='concat4')
            predict4 = slim.conv2d(concat4, 2, [3, 3], 1, 'SAME', activation_fn=None, scope='predict4')
            # 48 * 64 flow
            deconv3 = slim.conv2d_transpose(concat4, 128, [4, 4], 2, 'SAME', scope='deconv3')
            deconvflow4 = slim.conv2d_transpose(predict4, 2, [4, 4], 2, 'SAME', scope='deconvflow4')
            concat3 = tf.concat([conv3_1, deconv3, deconvflow4], 3, name='concat3')
            predict3 = slim.conv2d(concat3, 2, [3, 3], 1, 'SAME', activation_fn=None, scope='predict3')
            # 96 * 128 flow
            deconv2 = slim.conv2d_transpose(concat3, 64, [4, 4], 2, 'SAME', scope='deconv2')
            deconvflow3 = slim.conv2d_transpose(predict3, 2, [4, 4], 2, 'SAME', scope='deconvflow3')
            concat2 = tf.concat([conv2, deconv2, deconvflow3], 3, name='concat2')
            predict2 = slim.conv2d(concat2, 2, [3, 3], 1, 'SAME', activation_fn=None, scope='predict2')
            # 192 * 256 flow
            deconv1 = slim.conv2d_transpose(concat2, 64, [4, 4], 2, 'SAME', scope='deconv1')
            deconvflow2 = slim.conv2d_transpose(predict2, 2, [4, 4], 2, 'SAME', scope='deconvflow2')
            concat1 = tf.concat([conv1, deconv1, deconvflow2], 3, name='concat1')
            predict1 = slim.conv2d(concat1, 2, [3, 3], 1, 'SAME', activation_fn=None, scope='predict1')

        self.tvars = tf.trainable_variables()  # turn on if you want to check the variables
        # self.variables_names = [v.name for v in self.tvars]

        with tf.variable_scope('loss'):
            weight = [1.0/2, 1.0/4, 1.0/8, 1.0/16, 1.0/32, 1.0/32]
            flow6 = tf.image.resize_images(self.x3, [6, 8])
            loss6 = weight[5] * self.mean_loss(flow6, predict6)
            flow5 = tf.image.resize_images(self.x3, [12, 16])
            loss5 = weight[4] * self.mean_loss(flow5, predict5)
            flow4 = tf.image.resize_images(self.x3, [24, 32])
            loss4 = weight[3] * self.mean_loss(flow4, predict4)
            flow3 = tf.image.resize_images(self.x3, [48, 64])
            loss3 = weight[2] * self.mean_loss(flow3, predict3)
            flow2 = tf.image.resize_images(self.x3, [96, 128])
            loss2 = weight[1] * self.mean_loss(flow2, predict2)
            flow1 = tf.image.resize_images(self.x3, [192, 256])
            loss1 = weight[0] * self.mean_loss(flow1, predict1)
            self.loss = tf.add_n([loss6, loss5, loss4, loss3, loss2, loss1])
            tf.summary.scalar('loss6', loss6)
            tf.summary.scalar('loss5', loss5)
            tf.summary.scalar('loss4', loss4)
            tf.summary.scalar('loss3', loss3)
            tf.summary.scalar('loss2', loss2)
            tf.summary.scalar('loss1', loss1)
            tf.summary.scalar('loss', self.loss)
            # pdb.set_trace()
            # self.merged = tf.merge_all_summaries()
            self.merged = tf.summary.merge_all()
        optimizer = tf.train.AdamOptimizer(self.lr)
        self.train_op = slim.learning.create_train_op(self.loss, optimizer)

        # gpu configuration
        # self.tf_config = tf.ConfigProto()
        # self.tf_config = tf.ConfigProto(device_count = {'GPU': 0})
        self.tf_config = tf.ConfigProto(log_device_placement=True)
        self.tf_config.gpu_options.allow_growth = True
        # if use_gpu_1:
        #     self.tf_config.gpu_options.visible_device_list = '2,3'

        # pdb.set_trace()

        # self.init_all = tf.initialize_all_variables()
        self.init_all = tf.global_variables_initializer()

    def mean_loss(self, gt, predict):
        loss = tf.reduce_mean(tf.abs(gt-predict))
        return loss


def main(_):
    print('TensorFlow Version', tf.__version__)

    # data preparation
    list1_t, list2_t, list3_t, list1_v, list2_v, list3_v = load_data()
    dataset_t = Data(list1_t, list2_t, list3_t, shuffle=True, minus_mean=False)
    dataset_v = Data(list1_v, list2_v, list3_v, shuffle=True, minus_mean=False)
    x1_v = []
    x2_v = []
    x3_v = []
    for j in range(val_iter):
        x1_b, x2_b, x3_b = dataset_v.next_batch()
        x1_v.append(x1_b)
        x2_v.append(x2_b)
        x3_v.append(x3_b)

    model = Net(use_gpu_1=use_gpu_1)
    saver = tf.train.Saver(max_to_keep=max_to_keep)
    with tf.Session(config=model.tf_config) as sess:
        from tensorflow.python.client import device_lib
        device_lib.list_local_devices()

        print('session run\n')
        sess.run(model.init_all)
        
        print('model restore\n')
        saver.restore(sess, dir_restore)

        writer_train = tf.summary.FileWriter(dir_log_train, sess.graph)
        writer_val = tf.summary.FileWriter(dir_log_test, sess.graph)
        # pdb.set_trace()

        print('epoch start\n')

        for epoch in range(epoch_max):
            lr_decay = 0.1 ** (epoch / epoch_lr_decay)
            lr = lr_base * lr_decay
            for iteration in range(iter_per_epoch):
                time_start = time.time()
                global_iter = epoch * iter_per_epoch + iteration
                x1_t, x2_t, x3_t = dataset_t.next_batch()
                feed_dict = {model.x1: x1_t, model.x2: x2_t, model.x3: x3_t, model.lr: lr}
                _, merged_out_t, loss_out_t = sess.run([model.train_op, model.merged, model.loss], feed_dict)

                writer_train.add_summary(merged_out_t, global_iter + 1)
                hour_per_epoch = iter_per_epoch * ((time.time() - time_start) / 3600)
                print('%.2f h/epoch, epoch %03d/%03d, iter %04d/%04d, lr %.5f, loss: %.5f' %
                      (hour_per_epoch, epoch + 1, epoch_max, iteration + 1, iter_per_epoch, lr, loss_out_t))

                if not (iteration + 1) % 20:
                    feed_dict_v = {model.x1: x1_v[0], model.x2: x2_v[0], model.x3: x3_v[0]}
                    merged_out_v, loss_out_v = sess.run([model.merged, model.loss], feed_dict_v)
                    print('****val loss****: %.5f' % loss_out_v)
                    writer_val.add_summary(merged_out_v, global_iter + 1)

            # save
            if not (epoch + 1) % epoch_save:
                saver.save(sess, (dir_model + '/model'), global_step=epoch+1)


if __name__ == "__main__":
    tf.app.run()
