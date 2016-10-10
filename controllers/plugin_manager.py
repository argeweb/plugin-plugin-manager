#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from google.appengine.api import namespace_manager
from argeweb import route_with, route_menu
from argeweb import Controller, scaffold
import datetime
from google.appengine.api import memcache


class PluginManager(Controller):
    class Meta:
        pagination_actions = ("list", "pickup_list",)
        pagination_limit = 10

    class Scaffold:
        display_properties_in_list = ("theme_name", "theme_key")

    @route_with('/admin/plugin_manager/set.json')
    def admin_get_url(self):
        self.meta.change_view('json')
        plugin = self.params.get_string("plugin", '')
        action = self.params.get_string("action", '')
        enable_plugins_list = self.plugins.get_enable_plugins_from_db(self.server_name, self.namespace)
        prohibited_actions = self.prohibited_actions

        if "admin:"+plugin+":plugins_check" in prohibited_actions:
            self.context['data'] = {'info': "403", "plugin": plugin}
            return
        if action == u"enable":
            if plugin not in enable_plugins_list:
                enable_plugins_list.append(plugin)
        else:
            if plugin in enable_plugins_list:
                enable_plugins_list.remove(plugin)
        self.plugins.set_enable_plugins_to_db(self.server_name, self.namespace, enable_plugins_list)
        self.context['data'] = {'info': "done", "plugin": plugin}


    @route_menu(list_name=u"backend", text=u"模組管理", sort=9994, icon="gears", group=u"系統設定")
    @route_with('/admin/plugin_manager/pickup_list')
    def admin_pickup_list(self):
        scaffold.list(self)
        plugin_list = []
        enable_plugins_list = self.plugins.get_enable_plugins_from_db(self.server_name, self.namespace)
        prohibited_actions = self.prohibited_actions
        for item in self.plugins.get_all_plugin():
            module_path = 'plugins.%s' % item
            try:
                module = __import__('%s' % module_path, fromlist=['*'])
                cls = getattr(module, 'plugins_helper')
                cls["name"] = item
                cls["enable"] = True if item in enable_plugins_list else False
                cls["can_enable"] = False if "admin:"+item+":plugins_check" in prohibited_actions else True
                if "icon" not in cls:
                    cls["icon"] = "cube"
                plugin_list.append(cls)
            except:
                self.logging.debug("Plugins %s helper not found, skipping" % item)
        self.context["plugin_list"] = plugin_list
