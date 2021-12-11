
import os
from shrutitg.shrutitgbot import *
import time

if __name__ == "__main__":
    while True:
        shrutitgbot.logger.info("Cycle")
        activecalls = os.popen("asterisk -x 'core show channels verbose' | grep 'active calls'").read().strip()
        if activecalls != "0 active calls":
            shrutitgbot.logger.info("Skipping cycle since call in progress")
            time.sleep(180)
            continue
        try:
            call_list = os.listdir("/opt/shruti-ivr/calls")
            call_list.remove("calllog")
            for call in call_list:
                files = os.listdir(os.path.join(
                    "/opt/shruti-ivr/calls", call))
                if "telegramed" in files:
                    shrutitgbot.logger.info("Ignoring {}".format(call))
                    continue
                for fn in files:
                    if ".wav" in fn:
                        shrutitgbot.logger.info(
                            "Trying to upload {}".format(call))
                        shrutitgbot.updater.bot.send_audio(-456601244, open(
                            os.path.join("/opt/shruti-ivr/calls", call, fn), "rb"), caption=call, timeout=300)
                        with open(os.path.join(os.path.join("/opt/shruti-ivr/calls", call, "telegramed")), "w") as f:
                            f.write("Telegramed")
                        shrutitgbot.logger.info(
                            "Successfully uploaded {}".format(call))
        except Exception as e:
            shrutitgbot.logger.error("{} {}".format(str(e), repr(e)))
        time.sleep(180)
