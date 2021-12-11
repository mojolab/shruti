# syntax=docker/dockerfile:1
FROM ubuntu:latest
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
    libssl-dev
RUN sh -c "$(curl -fsSL https://hackergram.org/xpal/installxpal.sh)"
