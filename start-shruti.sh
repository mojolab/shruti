#!/usr/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS="/opt/shrutibot-appdata/shrutivoice.json"

# if /opt/shrutibot-appdata/shrutibottgtoken contains '<REPLACE WITH YOUR BOT TOKEN>' break script
if [ "$(cat /opt/shrutibot-appdata/shrutibottgtoken)" == "<REPLACE WITH YOUR BOT TOKEN>" ]; then
    echo "Please replace the token in /opt/shrutibot-appdata/shrutibottgtoken with your bot token"
    exit 0
fi

# if /opt/shrutibot-appdata/shrutivoice.json does not exist or is empty break script
if [ ! -s "/opt/shrutibot-appdata/shrutivoice.json" ]; then
    echo "Please copy the json file to /opt/shrutibot-appdata/shrutivoice.json"
    exit 0
fi  

# if /data/db does not exist, create it
if [ ! -d "/data/db" ]; then
    mkdir -p /data/db
    chmod a+rwx -R /data/db
fi


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
if ! pgrep -x runshrutibot.py > /dev/null; then
    cd /shruti/shrutibot/shrutixpal
    python3 runshrutibot.py &
fi

cd /shruti/shrutibot/shrutixpal

#ipython3 -i -- /shruti/shrutibot/shrutixpal/xpalshell.py