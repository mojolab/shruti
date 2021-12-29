# Shruti
Powerful listening at scale 

![image](https://user-images.githubusercontent.com/743783/147661243-e6a58536-d5e7-4036-9498-86b126cc1312.png)




## Installation Instructions

```
cd <shruti directory>

docker compose up

docker run -d -it --name shruti --mount type=bind,source=$PWD,target=/shruti shruti_core:latest

```

# Quick Start

```
cd /shruti

sh start-shruti.sh

```