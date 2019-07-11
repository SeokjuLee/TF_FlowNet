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
+ Download dataset
```Shell
cd dataset/FlyingChairs/data
./download_dataset.sh
```
+ Download models
```Shell
cd model/flownet_simple/755
./download_dataset.sh

cd ../333
./download_dataset.sh
```

+ run test_flownet_simple.py
```Shell
CUDA_VISIBLE_DEVICES=0 python3 test_flownet_simple.py
```



