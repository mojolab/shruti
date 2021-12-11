#!/usr/bin/zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

cp -arv xpalconfig/shrutibot-appdata /opt
cd /
sh -c "$(curl -fsSL https://hackergram.org/xpal/installxpal.sh)"
pip3 install mongoengine google-cloud-speech

cd /shruti/shrutibot/shrutixpal
ipython3 -i -- /shruti/shrutibot/shrutixpal/xpalshell.py