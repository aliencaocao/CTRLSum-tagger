# CTRLSum Tagger ONNX models and server
CTRLSum is a generic controllable summarization system to manipulate text summaries given control tokens in the form of keywords or prefix. CTRLsum is also able to achieve strong (e.g. state-of-the-art on CNN/Dailymail) summarization performance in an uncontrolled setting.

This repository contains the pretrained CTRLSum Tagger models and a simple flask server driver. Note that this repository does NOT contain the actual text summarization system. It only contains the tagger part of the system.

All models are original work of the authors of https://github.com/salesforce/ctrl-sum. I simply converted their pretrained models to ONNX format for faster loading and inference and greater compatibility.

After converting from the original PyTorch based model, the ONNX version can be accelerated by Nvidia TensorRT.

Currently, only the tagger model pretrained on the CNN/DailyMail dataset is available. For other planned models, please see the TODO section below.


## Prerequisites
Tested with Python 3.9.10 on Windows 10 and 3.8.12 on Ubuntu 18.04 LTS. It should work with any Python version officially supported by the packages specified in `requirements.txt`.

Tested with Nvidia CUDA 11.3 on Windows 10 and 10.2 on Ubuntu 18.04 LTS. Again, it should work with any CUDA version that the ONNX GPU Runtime supports. Note that different version of the `onnxruntime-gpu` library supports different version of CUDA and TensorRT. Please see here: https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html


## Python Usage
Note: Skip steps 3 & 4 if you only want to run inference on CPU.
1. Clone this repository
2. Run `pip install -r requirements.txt`
3. Run `pip uninstall -y onnxruntime`
4. Run `pip install onnxruntime-gpu`
5. Download the pretrained model from the Downloads section below.
6. Run `python tagger-server.py` to launch the flask server. Default hosting IP is 0.0.0.0 and port is 8080, however you can change them in `tagger-server.py`.
7. Run `python client-demo.py` to test the server. Before running, change the `url` line to your own computer's private ip address.


## Docker Usage
Note: The docker image below assumes that a compatible NVIDIA GPU is available. You can modify the base docker to switch CUDA versions. However, take note of version compatibility between the installed version of `onnxruntime-gpu` and CUDA version.
1. Clone this repository
2. Download the pretrained model from the Downloads section below.
3. Run `docker build . -t ctrl-sum-tagger-onnx:latest`
4. Run `docker run -p 8080:8080 ctrl-sum-tagger-onnx:latest`


## Offline Deployment
This repository was primarily built for a project that requires completely offline deployment of this tagger model. Thus, I have pre-downloaded the cache files required by the HuggingFace transformers library in the `cache` folder. Please do not delete or rename the folder and any file inside it if you want to deploy the model offline.

You can toggle offline or online mode in tagger-server.py by setting `offline_mode`. If `offline_mode` is set to `False`, HuggingFace will download and overwrite existing cache each time the server starts.


## Downloads
The following model weights are available for download currently:

| Model (Format) |                           Link                            |
|:--------------:|:---------------------------------------------------------:|
|   CNNDM ONNX   | https://1drv.ms/u/s!AvJPuRJUdWx_8B_D9VVnl9Pqokv_?e=KKbb1x |

After downloading, create a folder named `onnx_model` in the root directory of this repository and place the downloaded model file inside. Otherwise, you can modify the `tagger-server.py` to customize the path to model.


## TODO
* Add ONNX model pretrained on the arXiv dataset
* Add ONNX model pretrained on the BIGPATENT dataset
* Fix issue with alignment of tokens - currently, the generated tags may not match exactly with the original text
* Enable support for input text of more than 512 tokens