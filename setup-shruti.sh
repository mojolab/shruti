#!/usr/bin/zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# if /opt/shrutibot-appdata does not exist copy it over
if [ ! -d "/opt/shrutibot-appdata" ]; then
    cp -arv xpalconfig/shrutibot-appdata /opt
fi

cd /
sh -c "$(curl -fsSL https://hackergram.org/xpal/installxpal.sh)"
pip3 install mongoengine google-cloud-speech

# if mongod is not running, start mongod
if ! pgrep -x mongod > /dev/null
then
    mongod --dbpath /data/db --logappend --fork --logpath /data/db/mongod.log
fi

# if shrutiapi.py is not running run it
if ! pgrep -x shrutiapi.py > /dev/null
then
    cd /shruti
    python3 shrutiapi.py &
fi

# if runshrutibot.py is not running start it
if ! pgrep -x runshrutibot.py > /dev/null
then
    cd /shruti/shrutibot/shrutixpal
    python3 runshrutibot.py &
fi

cd /shruti/shrutibot/shrutixpal

ipython3 -i -- /shruti/shrutibot/shrutixpal/xpalshell.py