#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.


plugins_helper = {
    "title": u"模組管理",
    "desc": u"啟用或停用特定功能模組",
    "controllers": {
        "plugin_manager": {
            "group": u"模組管理",
            "actions": [
                {"action": "pickup_list", "name": u"進入模組管理畫面"},
                {"action": "plugins_check", "name": u"啟用停用模組"},
            ]
        }
    }
}