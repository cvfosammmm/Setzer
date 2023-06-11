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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class AnimatedPaned(object):

    def __init__(self, widget1, widget2, animate_first_widget=True):
        self.animate_first_widget = animate_first_widget
        if animate_first_widget:
            self.pack1(widget1, False, True)
            self.pack2(widget2, True, False)
            self.animated_widget = widget1
            self.fixed_widget = widget2
        else:
            self.pack1(widget1, True, False)
            self.pack2(widget2, False, True)
            self.animated_widget = widget2
            self.fixed_widget = widget1

        self.is_initialized = False
        self.animation_id = None
        self.is_visible = None
        self.show_widget = False
        self.animated_widget_extent = 0
        self.target_position = None

        self.animated_widget.connect('size-allocate', self.on_size_allocate)
        self.connect('size-allocate', self.on_size_allocate)
        self.connect('draw', self.on_realize)

    def on_realize(self, view=None, cr=None, user_data=None):
        if not self.is_initialized:
            self.animate(False)
            self.is_initialized = True

    def on_size_allocate(self, widget, allocation):
        if not self.is_initialized: return
        if not self.show_widget: return
        if self.animation_id != None: return

        new_extent = self.get_animated_widget_extent()
        self.animated_widget_extent = new_extent

        if self.animate_first_widget:
            self.set_target_position(new_extent)
        else:
            self.set_target_position(self.get_paned_extent() - new_extent - 1)

    def set_target_position(self, position):
        self.target_position = position

    def set_show_widget(self, show_widget):
        self.show_widget = show_widget

    def set_is_visible(self, is_visible):
        self.is_visible = is_visible

    def animate(self, animate=False):
        if self.animation_id != None: self.remove_tick_callback(self.animation_id)
        elif self.is_visible == self.show_widget: return

        frame_clock = self.get_frame_clock()
        duration = 200

        if self.show_widget:
            end = self.target_position
        else:
            if self.animate_first_widget:
                end = 0
            else:
                end = self.get_paned_extent()

        if frame_clock != None and animate:
            if self.get_position() != end:
                if self.show_widget:
                    self.animated_widget.show()
                start = self.get_position()
                start_time = frame_clock.get_frame_time()
                end_time = start_time + 1000 * duration
                self.child_set_property(self.animated_widget, 'shrink', True)
                self.fix_animated_widget_size()
                self.animation_id = self.add_tick_callback(self.set_position_on_tick, (self.show_widget, start_time, end_time, start, end))
        else:
            if self.show_widget:
                self.child_set_property(self.animated_widget, 'shrink', False)
                self.animated_widget.show()
                self.set_is_visible(True)
            else:
                self.child_set_property(self.animated_widget, 'shrink', True)
                self.animated_widget.hide()
                self.set_is_visible(False)
            self.set_position(end)

    def set_position_on_tick(self, paned, frame_clock_cb, user_data):
        show_widget, start_time, end_time, start, end = user_data
        now = frame_clock_cb.get_frame_time()
        if now < end_time and paned.get_position() != end:
            t = self.ease((now - start_time) / (end_time - start_time))
            paned.set_position(int(start + t * (end - start)))
            return True
        else:
            paned.set_position(end)
            self.reset_animated_widget_size_request()
            if not show_widget:
                self.animated_widget.hide()
                self.set_is_visible(False)
            else:
                self.child_set_property(self.animated_widget, 'shrink', False)
                self.set_is_visible(True)
            self.animation_id = None
            return False

    def ease(self, time):
        return (time - 1)**3 + 1;


class AnimatedHPaned(Gtk.Paned, AnimatedPaned):

    def __init__(self, widget1, widget2, animate_first_widget=True):
        Gtk.Paned.__init__(self, orientation = Gtk.Orientation.HORIZONTAL)
        AnimatedPaned.__init__(self, widget1, widget2, animate_first_widget)

        self.original_size_request = self.animated_widget.get_size_request()[0]

    def reset_animated_widget_size_request(self):
        self.animated_widget.set_size_request(self.original_size_request, -1)

    def fix_animated_widget_size(self):
        self.animated_widget.set_size_request(self.get_animated_widget_extent(), -1)

    def get_animated_widget_extent(self):
        return self.animated_widget.get_allocated_width()

    def get_paned_extent(self):
        return self.get_allocated_width()


class AnimatedVPaned(Gtk.Paned, AnimatedPaned):

    def __init__(self, widget1, widget2, animate_first_widget=True):
        Gtk.Paned.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        AnimatedPaned.__init__(self, widget1, widget2, animate_first_widget)

        self.original_size_request = self.animated_widget.get_size_request()[1]

    def reset_animated_widget_size_request(self):
        self.animated_widget.set_size_request(-1, self.original_size_request)

    def fix_animated_widget_size(self):
        self.animated_widget.set_size_request(-1, self.get_animated_widget_extent())

    def get_animated_widget_extent(self):
        return self.animated_widget.get_allocated_height()

    def get_paned_extent(self):
        return self.get_allocated_height()


