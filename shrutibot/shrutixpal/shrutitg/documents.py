# -*- coding: utf-8 -*-
"""
Created on Sat Sep  8 21:52:07 2018

@author: arjun
"""

from mongoengine import Document, fields, DynamicDocument
import datetime
import bson
import json
from flask_mongoengine import BaseQuerySet
from . import utils


class PPrintMixin(object):
    def __str__(self):
        return '<{}: id={!r}>'.format(type(self).__name__, self.id)

    def __repr__(self):
        attrs = []
        for name in self._fields.keys():
            value = getattr(self, name)
            if isinstance(value, (Document, DynamicDocument)):
                attrs.append('\n    {} = {!s},'.format(name, value))
            elif isinstance(value, (datetime.datetime)):
                attrs.append('\n    {} = {},'.format(
                    name, value.strftime("%Y-%m-%d %H:%M:%S")))
            else:
                attrs.append('\n    {} = {!r},'.format(name, value))
        return '<{}: {}\n>'.format(type(self).__name__, ''.join(attrs))


class CustomQuerySet(BaseQuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))


class Member(PPrintMixin, DynamicDocument):
    meta = {'queryset_class': BaseQuerySet}
    mobile_num = fields.StringField(unique=True, required=True)
    username = fields.StringField(unique=True, required=True)
    repayments = fields.DictField()
    tgid = fields.IntField()

    def __repr__(self):
        return "Member (%r)" % (self.username)


class Customer(PPrintMixin, DynamicDocument):
    meta = {'queryset_class': BaseQuerySet}
    cust_id = fields.StringField(unique=True, required=True)
    cust_type = fields.StringField()
    mobile_num = fields.StringField(required=True)
    tgid = fields.IntField()
    cust_billing = fields.StringField(default="N/A")
    cust_gstin = fields.StringField(default="N/A")
