#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from google.appengine.ext import ndb


class PluginManagerModel(BasicModel):
    class Meta:
        label_name = {
            "theme_name": u"樣式名稱",
            "theme_key": u"識別名稱",
            "exclusive": u"專屬項目",
            "is_enable": u"顯示於前台",
            "content": u"描述 "
        }
    theme_name = Fields.StringProperty(required=True)
    theme_key = Fields.StringProperty(required=True)
    exclusive = Fields.StringProperty(default="all")
    is_enable = Fields.BooleanProperty(default=True)
    content = Fields.RichTextProperty()

    @classmethod
    def get_by_theme_key(cls, theme_key):
        return cls.query(cls.theme_key == theme_key).get()

    @classmethod
    def get_list(cls, identifier_name):
        return cls.query(
            cls.exclusive.IN([identifier_name, u"all"])
        ).order(-cls.sort, -cls._key)

    @classmethod
    def check_in_list(cls, identifier_name, theme_key):
        item = cls.query(
            ndb.AND(
                cls.exclusive.IN([identifier_name, u"all"]),
                cls.theme_key == theme_key
            )
        ).order(-cls.sort, -cls._key).get()
        if item:
            return True
        else:
            return False
