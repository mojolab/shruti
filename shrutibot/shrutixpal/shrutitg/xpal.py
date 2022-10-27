# -*- coding: utf-8 -*-
#

"""
Created on Sat Sep  8 21:52:07 2018

@author: arjun
"""

import datetime
import json
import mongoengine
import xetrapal
import pandas
from . import documents, utils
from copy import deepcopy
import requests

from xetrapal import gdastras
from xetrapal import smsastras
a = xetrapal.karma.load_xpal_smriti(
    "/opt/shrutibot-appdata/shrutibotxpal.json")
a.save()
a.reload()
shrutitgbotxpal = xetrapal.Xetrapal(a)
shrutitgbotxpal.dhaarana(gdastras)
shrutitgbotxpal.dhaarana(smsastras)
#shrutitgbotgd = shrutitgbotxpal.gd_get_googledriver()
#sms = shrutitgbotxpal.get_sms_astra()
#sconfig = xetrapal.karma.load_config(a.configfile)
#mmiurl = sconfig.get("MapMyIndia", "apiurl")
#mmikey = sconfig.get("MapMyIndia", "apikey")
#mmiurl = mmiurl + mmikey + "/"

# Setting up mongoengine connections
shrutitgbotxpal.logger.info("Setting up MongoEngine")
mongoengine.disconnect()
mongoengine.connect('shrutitgbot', alias='default')

def validate_member_dict(memberdict, new=True):
    validation = {}
    validation['status'] = True
    validation['message'] = "Valid member"
    required_keys = []
    if new is True:
        required_keys = ["username", "mobile_num"]
    string_keys = ["first_name", "last_name",
                   "mobile_num", "name", "username"]
    mobile_nums = ["mobile_num"]
    validation = utils.validate_dict(
        memberdict, required_keys=required_keys, string_keys=string_keys, mobile_nums=mobile_nums)
    if validation['status'] is True:
        shrutitgbotxpal.logger.info("memberdict: " + validation['message'])
    else:
        shrutitgbotxpal.logger.error("memberdict: " + validation['message'])
    return validation


def get_member_by_mobile(mobile_num):
    t = documents.Member.objects(mobile_num=mobile_num)
    xetrapal.astra.baselogger.info(
        "Found {} members with Mobile Num {}".format(len(t), mobile_num))
    if len(t) > 0:
        # return[User(x['value']) for x in t][0]
        return t[0]
    else:
        return None


def get_member_by_username(username):
    t = documents.Member.objects(username=username)
    xetrapal.astra.baselogger.info(
        "Found {} members with Username{}".format(len(t), username))
    if len(t) > 0:
        # return[User(x['value']) for x in t][0]
        return t[0]
    else:
        return None


def get_member_by_tgid(tgid):
    t = documents.Member.objects(tgid=tgid)
    xetrapal.astra.baselogger.info(
        "Found {} members with Telegram username {}".format(len(t), tgid))
    if len(t) > 0:
        # return[User(x['value']) for x in t][0]
        return t[0]
    else:
        return None


def create_member(respdict):
    member = documents.Member.objects(username=respdict['username'])
    if len(member) > 0:
        return "Member with that username exists"
    if "_id" in respdict.keys():
        respdict.pop('_id')
    try:
        member = documents.Member(**respdict)
        member.save()
        return [member]
    except Exception as e:
        return "{} {}".format(repr(e), str(e))


def update_member(username, respdict):
    member = documents.Member.objects(username=username)
    if len(member) == 0:
        return "No member by username {}".format(username)
    else:
        member = member[0]
    if "_id" in respdict.keys():
        respdict.pop('_id')
    if "username" in respdict.keys():
        if respdict['username'] != username:
            return "Member username mismatch {} {}".format(username, respdict['username'])
        respdict.pop('username')
    try:
        member.update(**respdict)
        member.save()
        member.reload()
        return [member]
    except Exception as e:
        return "{} {}".format(type(e), str(e))


def update_member_repayments(repayments):
    for r in repayments:
        mem = documents.Member.objects(username=r['from'])[0]
        shrutitgbotxpal.logger.info(mem.to_json())
        mem['repayments'][r['to']] += r['amount']
        mem.save()
        shrutitgbotxpal.logger.info(mem.to_json())
        mem2 = documents.Member.objects(username=r['to'])[0]
        shrutitgbotxpal.logger.info(mem2.to_json())
        mem2['repayments'][r['from']] += -r['amount']
        mem2.save()
        shrutitgbotxpal.logger.info(mem2.to_json())

def update_member_balance(members):
    for member in members:
        mem = documents.Member.objects(username=member['username']).update(inc__net_balance = member['net_balance'])

def delete_member(username):
    if len(documents.Member.objects(username=username)) > 0:
        try:
            member = documents.Member.objects(username=username)[0]
            member.delete()
            return []
        except Exception as e:
            return "{} {}".format(type(e), str(e))
    else:
        return "No member by that id"




