# syntax=docker/dockerfile:1
FROM ubuntu:latest
ENV DEBIAN_FRONTEND="noninteractive" TZ="Asia/Kolkata"
# Install Xetrapal Dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ipython3 \
    python3-dev \
    zsh \
    git \
    vim \
    curl \
    sudo \
    wget \
    build-essential \
    libssl-dev \
    net-tools \
    openssh-server \
    --fix-missing
RUN mkdir /shruti
# RUN sh -c "$(curl -fsSL https://hackergram.org/xpal/installxpal.sh)"
# RUN cp -arv /shruti/xpalconfig/shrutibot-appdata /opt 