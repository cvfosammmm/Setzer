#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject


class BuildWidgetView(Gtk.HBox):
    ''' Shows how long the build process takes '''
    
    def __init__(self):
        Gtk.HBox.__init__(self)
        self.get_style_context().add_class('build-widget')

        self.timer = 0
        self.timer_active = False
        self.state_change_count = 0
        
        self.build_button = Gtk.Button.new_from_icon_name('builder-build-symbolic', Gtk.IconSize.MENU)
        self.build_button.set_focus_on_click(False)
        self.build_button.set_tooltip_text('Build .pdf-file from document (F6)')

        self.stop_button = Gtk.Button.new_from_icon_name('process-stop-symbolic', Gtk.IconSize.MENU)
        self.stop_button.set_focus_on_click(False)
        self.stop_button.set_tooltip_text('Stop building')

        self.clean_button = Gtk.Button.new_from_icon_name('edit-clear-all-symbolic', Gtk.IconSize.MENU)
        self.clean_button.set_focus_on_click(False)
        self.clean_button.set_tooltip_text('Cleanup build files')

        self.build_timer = Gtk.Revealer()
        self.build_timer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.build_timer_wrapper = Gtk.VBox()
        self.build_timer_wrapper.pack_start(Gtk.DrawingArea(), True, True, 0)
        self.label = Gtk.Label('')
        self.label.get_style_context().add_class('build-timer')
        self.label.set_xalign(0)
        self.build_timer_wrapper.pack_start(self.label, False, False, 0)
        self.build_timer_wrapper.pack_start(Gtk.DrawingArea(), True, True, 0)
        self.build_timer.add(self.build_timer_wrapper)

        self.pack_start(self.build_timer, False, False, 0)
        self.pack_start(self.build_button, False, False, 0)
        self.pack_start(self.stop_button, False, False, 0)
        self.pack_start(self.clean_button, False, False, 0)

        self.show_all()
        
    def start_timer(self):
        self.timer_active = True
        GObject.timeout_add(50, self.increment_timer)
        
    def increment_timer(self):
        if self.timer_active:
            self.timer += 50
            if self.timer // 1000 >= 1:
                self.label.set_text('{}:{:02}'.format(self.timer // 60000, (self.timer % 60000) // 1000))
                self.set_size_request(max(self.label.get_allocated_width(), self.label.get_size_request()[0]), -1)
        return self.timer_active

    def stop_timer(self):
        self.timer_active = False

    def reset_timer(self):
        self.timer = 0
        self.label.set_text('')
        self.build_timer.set_size_request(-1, -1)
    
    def show_timer(self):
        self.state_change_count += 1
        GObject.timeout_add(5, self.reveal, self.state_change_count)
        
    def show_result(self, text=''):
        self.label.set_markup(text)
        self.build_timer.set_size_request(max(self.label.get_allocated_width(), self.label.get_size_request()[0]), -1)
    
    def has_result(self):
        text = self.label.get_text()
        if text[:6] in ['Succes', 'Failed']:
            return True
        else:
            return False
        
    def hide_timer(self, duration):
        self.state_change_count += 1
        GObject.timeout_add(duration, self.unreveal, self.state_change_count)
        
    def reveal(self, state_change_count):
        if self.state_change_count == state_change_count:
            self.build_timer.set_reveal_child(True)
        return False

    def unreveal(self, state_change_count):
        if self.state_change_count == state_change_count:
            self.build_timer.set_reveal_child(False)
        return False


