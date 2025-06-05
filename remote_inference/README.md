# Remote Inference Server Setup Guide

This guide walks you through setting up a remote inference server on high-end GPUs (3090/4090/5090) and connecting to it from your MacBook Pro. 
Similar Implementations 
* from Isaac-GR00T: https://github.com/NVIDIA/Isaac-GR00T/blob/main/scripts/inference_service.py#:20, https://github.com/NVIDIA/Isaac-GR00T/blob/main/gr00t/eval/robot.py
* from OpenPi: https://github.com/Physical-Intelligence/openpi/tree/main/src/openpi

## 1. Eval ACT Model on Robot (so-arm100)

First, copy the config files:
```
cp -r /Users/danqingzhang/lerobot/.cache /Users/danqingzhang/Desktop/learning/awesome-lerobot/remote-inference/
```
then
```
cd act_soarm100
```

### Run Inference on the Server

On the server, run:
```
python websocket_server_act.py
```
then establish port forwarding like
```
ssh -i ~/.ssh/id_donnager -p 2022 -L 8765:localhost:8765 ib@donnager -N
```

### On MacBook
run:
```
python adhoc_eval_robot_act.py
```


## 2. Eval pi0
[![Watch the video](https://img.youtube.com/vi/Fuf9Kqy5tpk/hqdefault.jpg)](https://www.youtube.com/embed/Fuf9Kqy5tpk)

### Run Inference on the Server

On the server, run:
```
python websocket_server_pi0.py
```
then establish port forwarding like
```
ssh -i ~/.ssh/id_donnager -p 2022 -L 8765:localhost:8765 ib@donnager -N
```

### On MacBook
run:
```
python adhoc_eval_robot_pi0.py
```

## 3. Eval SmolVLA
### Run Inference on the Server

On the server, run:
```
python websocket_server_smolvla.py
```
then establish port forwarding like
```
ssh -i ~/.ssh/id_donnager -p 2022 -L 8765:localhost:8765 ib@donnager -N
```

### On MacBook
run:
```
python adhoc_eval_robot_smolvla.py
```


