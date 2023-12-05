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
from gi.repository import Gtk, GObject


class BuildWidgetView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.get_style_context().add_class('build-widget')
        self.set_can_focus(False)

        self.timer = 0
        self.timer_active = False
        self.state_change_count = 0
        
        self.build_button = Gtk.Button()
        self.build_button.set_child(Gtk.Image.new_from_icon_name('builder-build-symbolic'))
        self.build_button.set_tooltip_text(_('Save and build .pdf-file from document') + ' (F5)')
        self.build_button.set_action_name('win.save-and-build')

        self.stop_button = Gtk.Button()
        self.stop_button.set_child(Gtk.Image.new_from_icon_name('process-stop-symbolic'))
        self.stop_button.set_tooltip_text(_('Stop building'))

        self.clean_button = Gtk.Button()
        self.clean_button.set_child(Gtk.Image.new_from_icon_name('brush-symbolic'))
        self.clean_button.set_tooltip_text(_('Cleanup build files'))

        self.build_timer = Gtk.Revealer()
        self.build_timer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.label = Gtk.Label.new('')
        self.label.get_style_context().add_class('build-timer')
        self.build_timer.set_child(self.label)

        self.prepend(self.clean_button)
        self.prepend(self.build_button)
        self.prepend(self.stop_button)
        self.prepend(self.build_timer)
        
    def start_timer(self):
        self.timer_active = True
        GObject.timeout_add(50, self.increment_timer)
        
    def increment_timer(self):
        if self.timer_active:
            self.timer += 50
            if self.timer // 1000 >= 1:
                self.label.set_text('{}:{:02}'.format(self.timer // 60000, (self.timer % 60000) // 1000))
        return self.timer_active

    def stop_timer(self):
        self.timer_active = False

    def reset_timer(self):
        self.timer = 0
        self.label.set_text('')

    def show_timer(self):
        self.build_timer.set_visible(True)
        self.state_change_count += 1
        GObject.timeout_add(5, self.reveal, self.state_change_count)
        
    def show_result(self, text=''):
        self.label.set_markup(text)
    
    def has_result(self):
        text = self.label.get_text()
        if text[:6] in ['Succes', 'Failed']:
            return True
        else:
            return False
        
    def hide_timer(self, duration):
        self.state_change_count += 1
        GObject.timeout_add(duration, self.unreveal, self.state_change_count)
        
    def hide_timer_now(self):
        self.build_timer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        self.build_timer.set_reveal_child(False)
        self.build_timer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)

    def reveal(self, state_change_count):
        if self.state_change_count == state_change_count:
            self.build_timer.set_reveal_child(True)
        return False

    def unreveal(self, state_change_count):
        if self.state_change_count == state_change_count:
            self.build_timer.set_reveal_child(False)
        return False


