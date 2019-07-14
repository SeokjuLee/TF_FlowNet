# [filter size, stride, padding]
### Assume the two dimensions are the same
### Each kernel requires the following parameters:
# - k_i: kernel size
# - s_i: stride
# - p_i: padding (if padding is uneven, right padding will higher than left padding; "SAME" option in tensorflow)
# 
### Each layer i requires the following parameters to be fully represented: 
# - n_i: number of feature (data layer has n_1 = imagesize )
# - j_i: distance (projected to image pixel distance) between center of two adjacent features
# - r_i: receptive field of a feature in layer i
# - start_i: position of the first feature's receptive field in layer i (idx start from 0, negative means the center fall into padding)

import math
import pdb

convnet =   [[11,4,0],[3,2,0],[5,1,2],[3,2,0],[3,1,1],[3,1,1],[3,1,1],[3,2,0],[6,1,0], [1, 1, 0]]       # AlexNet
layer_names = ['conv1','pool1','conv2','pool2','conv3','conv4','conv5','pool5','fc6-conv', 'fc7-conv']  # AlexNet

# convnet =   [[7,2,0],[5,2,0],[5,2,0],[3,1,0],[3,2,0],[3,1,0],[3,2,0],[3,1,0],[3,2,0],[3,1,0],[3,1,0]] # FlowNet
# convnet =   [[3,2,0],[3,2,0],[3,2,0],[3,1,0],[3,2,0],[3,1,0],[3,2,0],[3,1,0],[3,2,0],[3,1,0],[3,1,0]] # FlowNet-SD
# layer_names = ['conv1','conv2','conv3','conv3_1','conv4','conv4_1','conv5','conv5_1','conv6','conv6_1','predict6']
# pdb.set_trace()

imsize = 512

def outFromIn(conv, layerIn):
  n_in = layerIn[0]       # resolution of input feature
  j_in = layerIn[1]       # input feature distance
  r_in = layerIn[2]       # input receptive field size
  start_in = layerIn[3]   # center position of the first feature in the previous layer
  k = conv[0]             # kernel size
  s = conv[1]             # stride size
  p = conv[2]             # padding size
  
  n_out = __________________________________    # resolution of output feature
  actualP = (n_out-1)*s - n_in + k                     
  pR = math.ceil(actualP/2)
  pL = math.floor(actualP/2)
  
  j_out = ________                              # output feature distance
  r_out = ___________________                   # output receptive field size
  start_out = start_in + ((k-1)/2 - pL)*j_in    # center position of the first feature in the current layer
  return n_out, j_out, r_out, start_out
  
def printLayer(layer, layer_name):
  print(layer_name + ":")
  print("\t n features: %s \n \t jump: %s \n \t receptive size: %s \t start: %s " % (layer[0], layer[1], layer[2], layer[3]))
  
layerInfos = []
if __name__ == '__main__':
#first layer is the data layer (image) with n_0 = image size; j_0 = 1; r_0 = 1; and start_0 = 0.5
  print ("-------Net summary------")
  currentLayer = [imsize, 1, 1, 0.5]
  printLayer(currentLayer, "input image")
  for i in range(len(convnet)):
    currentLayer = outFromIn(convnet[i], currentLayer)
    layerInfos.append(currentLayer)
    printLayer(currentLayer, layer_names[i])
  print ("------------------------")
  
  # pdb.set_trace()
