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
    "/opt/zhulibot-appdata/zhulibotxpal.json")
a.save()
a.reload()
zhulitgbotxpal = xetrapal.Xetrapal(a)
zhulitgbotxpal.dhaarana(gdastras)
zhulitgbotxpal.dhaarana(smsastras)
#zhulitgbotgd = zhulitgbotxpal.gd_get_googledriver()
#sms = zhulitgbotxpal.get_sms_astra()
#sconfig = xetrapal.karma.load_config(a.configfile)
#mmiurl = sconfig.get("MapMyIndia", "apiurl")
#mmikey = sconfig.get("MapMyIndia", "apikey")
#mmiurl = mmiurl + mmikey + "/"

# Setting up mongoengine connections
zhulitgbotxpal.logger.info("Setting up MongoEngine")
mongoengine.disconnect()
mongoengine.connect('zhulitgbot', alias='default')





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
        zhulitgbotxpal.logger.info("memberdict: " + validation['message'])
    else:
        zhulitgbotxpal.logger.error("memberdict: " + validation['message'])
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
        return "Driver with that username Exists"
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
        zhulitgbotxpal.logger.info(mem.to_json())
        mem['repayments'][r['to']] += r['amount']
        mem.save()
        zhulitgbotxpal.logger.info(mem.to_json())
        mem2 = documents.Member.objects(username=r['to'])[0]
        zhulitgbotxpal.logger.info(mem2.to_json())
        mem2['repayments'][r['from']] += -r['amount']
        mem2.save()
        zhulitgbotxpal.logger.info(mem2.to_json())

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



'''
Customer
'''


def create_customer(respdict):
    customer = documents.Customer.objects(cust_id=respdict['cust_id'])
    if len(customer) > 0:
        return "Customer with that username Exists"
    if len(respdict['cust_id']) < 5:
        return "id should be minimum of 5 characters"
    if "_id" in respdict.keys():
        respdict.pop('_id')
    try:
        customer = documents.Customer(**respdict)
        customer.save()
        return [customer]
    except Exception as e:
        return "{} {}".format(repr(e), str(e))


def update_customer(cust_id, respdict):
    customer = documents.Customer.objects(cust_id=cust_id)
    if len(customer) == 0:
        return "No Customer by username {}".format(cust_id)
    else:
        customer = customer[0]
    if "_id" in respdict.keys():
        respdict.pop('_id')
    if "cust_id" in respdict.keys():
        if respdict['cust_id'] != cust_id:
            return "customer username mismatch {} {}".format(cust_id, respdict['cust_id'])
        respdict.pop('cust_id')
    try:
        customer.update(**respdict)
        customer.save()
        customer.reload()
        return [customer]
    except Exception as e:
        return "{} {}".format(type(e), str(e))


def delete_customer(cust_id):
    if len(documents.Customer.objects(cust_id=cust_id)) > 0:
        try:
            customer = documents.Customer.objects(cust_id=cust_id)[0]
            customer.delete()
            return []
        except Exception as e:
            return "{} {}".format(type(e), str(e))
    else:
        return "No customer by that id"



'''
Xchanges
'''


def get_xchange(xchange_id=None):
    zhulitgbotxpal.logger.info((xchange_id))
    if xchange_id is None:
        try:
            xchange = documents.Xchange.objects
            return list(xchange)
        except Exception as e:
            return "{} {}".format(type(e), str(e))
    if len(documents.Xchange.objects(xchange_id=xchange_id)) > 0:
        try:
            xchange = documents.Xchange.objects(xchange_id=xchange_id)
            return [xchange]
        except Exception as e:
            return "{} {}".format(type(e), str(e))
    else:
        return "No such xchange"


def create_xchange(xchangedict):
    zhulitgbotxpal.logger.info(utils.new_xchange_id())
    try:
        xchange = documents.Xchange(
            xchange_id=utils.new_xchange_id(), **xchangedict)
        xchange.save()
        update_member_repayments(xchangedict['repayments'])
        update_member_balance(xchangedict['members'])
        return[xchange]
    except Exception as e:
        return "{} {}".format(type(e), str(e))


def update_xchange(xchange_id, xchangedict):
    try:
        if "_id" in xchangedict:
            xchangedict.pop("_id")
        xchange = documents.Xchange.objects(xchange_username=xchange_username)[0]
        xchange.update(**xchangedict)
        xchange.save()
        xchange.total = get_xchange_total(xchange.xchange_id)
        return[xchange]
    except Exception as e:
        return "{} {}".format(type(e), str(e))


def delete_xchange(xchange_id):
    if len(documents.Xchange.objects(xchange_id=xchange_id)) == 0:
        return "No Xchange by that username"
    else:
        try:
            xchange = documents.Xchange.objects(xchange_id=xchange_id)
            xchange.delete()
            return []
        except Exception as e:
            return "{} {}".format(type(e), str(e))




'''
Exporting everything
'''


def export_members():
    members = documents.Member.objects.to_json()
    members = json.loads(members)
    for member in members:
        del member['_id']
    memberdf = pandas.DataFrame(members)
    memberdf.to_csv("./dispatcher/reports/members.csv")
    return "reports/members.csv"

'''
Bulk Imports of everything
'''

def import_members(memberlist):
    try:
        for member in memberlist:
            try:
                if validate_member_dict(member)['status'] is True:
                    d = create_member(member)
                    if type(d) == list:
                        d = d[0]
                        d.save()
                        d.reload()
                        member['status'] = d.username
                    else:
                        member['status'] = d
                else:
                    member['status'] = validate_member_dict(member)['message']
            except Exception as e:
                member['status'] = "{} {}".format(type(e), str(e))
        return memberlist
    except Exception as e:
        return "{} {}".format(type(e), str(e))
