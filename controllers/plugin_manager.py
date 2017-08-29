#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from google.appengine.api import taskqueue
from google.appengine.api import app_identity
from argeweb import route_with, route_menu
from argeweb import Controller, scaffold


class PluginManager(Controller):
    class Meta:
        pagination_actions = ('list', 'pickup_list',)

    class Scaffold:
        display_in_list = ['theme_name', 'theme_key']

    @route_with('/admin/plugin_manager/set.json')
    def admin_set_plugin(self):
        self.meta.change_view('json')
        plugin = self.params.get_string('plugin', '')
        action = self.params.get_string('action', '')
        uri = self.params.get_string('uri', '')
        enable_plugins_list = self.host_information.plugins_list
        prohibited_actions = self.prohibited_actions

        if 'admin:'+plugin+':plugins_check' in prohibited_actions:
            self.context['data'] = {'info': '403', 'plugin': plugin}
            return
        if action == u'enable':
            if plugin not in enable_plugins_list:
                enable_plugins_list.append(plugin)
        else:
            if plugin in enable_plugins_list:
                enable_plugins_list.remove(plugin)
        if uri is not '':
            try:
                if uri.startswith('taskqueue:') is False:
                    uri = 'taskqueue:' + uri
                self.logging.info(uri)
                taskqueue.add(url=self.uri(uri), params={'plugin': plugin, 'action': action})
            except KeyError:
                pass
        self.plugins.set_enable_plugins_to_db(self.server_name, self.namespace, enable_plugins_list)

        self.context['data'] = {'info': 'done', 'plugin': plugin}

    @property
    def allowed_app_ids(self):
        return [app_identity.get_application_id() + '.appspot.com']

    @route_menu(list_name=u'super_user', text=u'模組管理', sort=1, group=u'模組管理')
    def admin_list(self):
        query = self.params.get_string('query', u'')
        scaffold.list(self)
        plugin_list = []
        enable_plugins_list = self.host_information.plugins_list
        prohibited_actions = self.prohibited_actions
        the_same_domain = False
        if self.server_name in self.allowed_app_ids or self.server_name.find('@'):
            the_same_domain = True
        for target_type in ['application', 'plugins']:
            for item in self.get_plugin_name_list_with_type(target_type):
                try:
                    module_path = '%s.%s' % (target_type, item)
                    if module_path == 'plugins.host_information' and the_same_domain is False:
                        continue
                    cls = getattr(__import__('%s' % module_path, fromlist=['*']), 'plugins_helper')
                    cls['name'] = module_path
                    cls['icon'] = cls['icon'] if 'icon' in cls else 'cube'
                    cls['enable'] = True if module_path in enable_plugins_list else False
                    cls['can_enable'] = False if 'admin:'+item+':plugins_check' in prohibited_actions else True

                    if self.cls_has_query_keyword(cls, query):
                        plugin_list.append(cls)
                except:
                    self.logging.debug('%s %s helper not found, skipping' % (target_type, item))
        self.context['plugin_list'] = plugin_list

    @staticmethod
    def cls_has_query_keyword(cls, query):
        need_append = False
        for k, v in cls.items():
            kv = k.find(query)
            if isinstance(v, basestring) and kv + v.find(query) > -2:
                need_append = True
        return need_append

    def get_plugin_name_list_with_type(self, target_type='plugins', use_cache=True):
        """
        取得所有的 controller
        """
        c = self.plugins.get_all_controller_with_type(target_type, use_cache)
        b = [item.split('.')[1] if item.find('.') > 0 else item for item in c]
        c = list(set(b))
        c.sort(key=b.index)
        return c

