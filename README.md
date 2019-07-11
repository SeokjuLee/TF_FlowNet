# TF_FlowNet
+ Original codes by [linjian93](https://github.com/linjian93/tf-flownet)


## Model links
+ [20190710_755_01](https://drive.google.com/open?id=1Ck9BK1m9mFv5cpMudbldok7VIkiYEvbp)
+ [20190710_333_01](https://drive.google.com/open?id=1LOMNKGGCp64OqLGXoIp8n1tKVD7C_YAA)


## Dependencies
```Shell
conda create -n SK_Week4_sfm tensorflow-gpu=1.8 ipython jupyter pillow ipykernel  gdbm anaconda -y

source  activate SK_Week4_sfm

conda install -c conda-forge matplotlib -y
conda install -c menpo opencv
conda install -c anaconda scipy
conda install tensorflow-gpu=1.8

python -m ipykernel install  --user --name SK_Week4_sfm --display-name "[SK_Week4_sfm]"
jupyter notebook
```

## Usage
1) Clone git
```Shell
git clone https://github.com/SeokjuLee/TF_FlowNet
cd TF_FlowNet
```

2) Download dataset
```Shell
cd dataset/FlyingChairs/data
chmod +x download_dataset.sh
./download_dataset.sh
cd ../../..
```

3) Download models
```Shell
cd model/flownet_simple/755
chmod +x download_model.sh
./download_model.sh
cd ../../..

cd model/flownet_simple/755
chmod +x download_model.sh
./download_model.sh
cd ../../..
```

4) Run test_flownet_simple.py
```Shell
CUDA_VISIBLE_DEVICES=0 python3 test_flownet_simple.py
```



