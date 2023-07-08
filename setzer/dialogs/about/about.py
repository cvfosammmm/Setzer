#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>


import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk

from setzer.app.service_locator import ServiceLocator


class AboutDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        self.view.show()
        del(self.view)

    def setup(self):
        self.view = Adw.AboutWindow.new()
        self.view.set_transient_for(self.main_window)
        self.view.set_modal(True)
        self.view.set_application_name('Setzer')
        self.view.set_version(ServiceLocator.get_setzer_version())
        self.view.set_copyright('Copyright © 2018-present')
        self.view.set_comments(_('Setzer is a LaTeX editor.'))
        self.view.set_license_type(Gtk.License.GPL_3_0)
        self.view.set_website('https://www.cvfosammmm.org/setzer/')
        self.view.set_developer_name('Robert Griesel')
        self.view.set_application_icon('org.cvfosammmm.Setzer')
        # TRANSLATORS: 'Name <email@domain.com>' or 'Name https://website.example'
        self.view.set_translator_credits(_('translator-credits'))
        self.view.set_issue_url('https://github.com/cvfosammmm/Setzer/issues')


