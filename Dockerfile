FROM nvidia/cuda:11.0-cudnn8-devel-ubuntu18.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

# Install Dependencies of Miniconda
RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 curl git sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda3
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate ale" >> ~/.bashrc

# Install munge for master node
RUN export MUNGEUSER=3456 && \
    groupadd -g $MUNGEUSER munge && \
    useradd  -m -c "MUNGE Uid 'N' Gid Emporium" -d /var/lib/munge -u $MUNGEUSER -g munge  -s /sbin/nologin munge && \
    apt update && apt install munge libmunge2 libmunge-dev && \
    create-munge-key -f && \
    sudo service munge start && \
    sudo service munge status && \
    chown -R munge: /etc/munge/ /var/log/munge/ /var/lib/munge/ /run/munge/ && \
    chmod 0700 /etc/munge/ /var/log/munge/ /var/lib/munge/ && \
    chmod 0755 /run/munge/ && \
    munge -n | unmunge

# Install Slurm
RUN export SLURMUSER=3457 && \
    groupadd -g $SLURMUSER slurm && \
    useradd  -m -c "SLURM workload manager" -d /var/lib/slurm -u $SLURMUSER -g slurm  -s /bin/bash slurm && \
    apt update && apt install -y slurm-wlm slurm-wlm-doc


# Install dependencies for MA-ALE project
RUN sudo apt-get update && sudo apt-get install -y default-libmysqlclient-dev libgl1-mesa-glx libglib2.0-0 tmux

COPY requirements.txt /tmp/requirements.txt
WORKDIR /tmp
RUN conda create -y -n ale python==3.8.12
SHELL ["/bin/bash", "-i", "-c"]
RUN conda activate ale && \
    pip install -r requirements.txt && \
    rm /tmp/requirements.txt && \
    AutoROM --accept-license

WORKDIR /workspaces