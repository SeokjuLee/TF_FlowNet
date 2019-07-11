# TF_FlowNet

## Model links
+ [20190710_755_01](https://drive.google.com/open?id=1Ck9BK1m9mFv5cpMudbldok7VIkiYEvbp)
+ [20190710_333_01](https://drive.google.com/open?id=1LOMNKGGCp64OqLGXoIp8n1tKVD7C_YAA)

```Shell
wget --no-check-certificate "download_link"
```

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
