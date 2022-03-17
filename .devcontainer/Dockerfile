# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.224.2/containers/python-3-miniconda/.devcontainer/base.Dockerfile

FROM mcr.microsoft.com/vscode/devcontainers/miniconda:0-3

RUN sudo apt-get update && sudo apt-get install -y default-libmysqlclient-dev libgl1-mesa-glx tmux
COPY requirements.txt /tmp/requirements.txt
WORKDIR /tmp
RUN conda create -y -n ale python==3.8.12
SHELL ["/bin/bash", "-i", "-c"]
RUN conda activate ale \
    && pip install -r requirements.txt \
    && rm /tmp/requirements.txt \
    && AutoROM --accept-license
