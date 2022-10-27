#!/usr/bin/bash

sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# if /opt/shrutibot-appdata does not exist copy it over
if [ ! -d "/opt/shrutibot-appdata" ]; then
    cp -arv xpalconfig/shrutibot-appdata /opt
fi

cd /
sh -c "$(curl -fsSL https://hackergram.org/xpal/installxpal.sh)"
apt install fortune -y
pip3 install mongoengine google-cloud-speech jupyterlab

