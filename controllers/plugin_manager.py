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
        can_disable_plugins_list = []
        all_installed = self.plugins_all
        plugin = self.params.get_string("plugin", '')
        action = self.params.get_string("action", '')
        enable_plugins_list = self.settings.get_plugins(self.server_name, self.namespace)

        for item in all_installed:
            try:
                if self.uri_exists_with_permission('admin:' + item + ":plugins_check"):
                    can_disable_plugins_list.append(item)
            except:
                self.logging.debug("Plugins %s no permission, skipping" % item)
        if plugin not in can_disable_plugins_list:
            self.context['data'] = {'info': "403", "plugin": plugin}
            return

        module_path = 'plugins.%s' % plugin
        try:
            module = __import__('%s' % module_path, fromlist=['*'])
            cls = getattr(module, 'plugins_helper')
            if "plugins_controller" in cls:
                plugins_controller_list = cls["plugins_controller"].split(",")
                if action == u"enable":
                    for plugins_loop_item in plugins_controller_list:
                        if plugins_loop_item not in enable_plugins_list:
                            enable_plugins_list.append(plugins_loop_item)
                else:
                    for plugins_loop_item in plugins_controller_list:
                        if plugins_loop_item in enable_plugins_list and plugin in can_disable_plugins_list:
                            enable_plugins_list.remove(plugins_loop_item)
        except:
            self.logging.debug("Plugins %s helper not found, skipping" % plugin)
        self.settings.set_plugins(self.server_name, self.namespace, enable_plugins_list)
        self.context['data'] = {'info': "done", "plugin": plugin}

    @route_menu(list_name=u"backend", text=u"模組管理", sort=9994, icon="gears", group=u"系統設定")
    @route_with('/admin/plugin_manager/pickup_list')
    def admin_pickup_list(self):
        scaffold.list(self)
        plugin_list = []
        enable_plugins_list = self.settings.get_plugins(self.server_name, self.namespace)
        self.logging.info(self.plugins_all)
        for item in self.plugins_all:
            module_path = 'plugins.%s' % item
            try:
                module = __import__('%s' % module_path, fromlist=['*'])
                cls = getattr(module, 'plugins_helper')
                cls["name"] = item
                if item in enable_plugins_list:
                    cls["enable"] = True
                else:
                    cls["enable"] = False
                if "icon" not in cls:
                    cls["icon"] = "cube"
                plugin_list.append(cls)
            except:
                self.logging.debug("Plugins %s helper not found, skipping" % item)
        self.context["plugin_list"] = plugin_list
