FROM nvidia/cuda:11.4.3-runtime-ubuntu20.04
WORKDIR /usr/src/app

# Install generic packages
RUN cp -a /etc/apt/sources.list /etc/apt/sources.list.bak && \
  apt-get update && \
  apt-get install -y python3.8 python3-distutils curl wget zip zlib1g && \
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
  python3.8 get-pip.py && \
  pip install -U setuptools wheel && \
  pip install flask waitress && \
  rm -rf /var/lib/apt/lists/* && \
  apt-get clean

# Install model-specific dependencies
RUN pip install transformers[onnxruntime] scipy && \
  pip uninstall -y onnxruntime && \
  pip install onnxruntime-gpu

# Copy code and model weights to working dir
COPY . .

# Clean up files
RUN rm /usr/src/app/Dockerfile /usr/src/app/get-pip.py && \
  pip cache purge

CMD ["python3.8", "tagger-server.py"]