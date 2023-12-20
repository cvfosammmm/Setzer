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

import time


class DocumentStructurePage(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)
        self.labels = dict()
        self.content_vbox_children = list()
        self.scroll_to = None

        self.content_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.content_vbox)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_can_focus(False)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.add_buttons()
        self.vbox.append(self.scrolled_window)
        self.set_child(self.vbox)

        self.scrolled_window.get_vadjustment().connect('changed', self.on_scroll_or_resize)
        self.scrolled_window.get_vadjustment().connect('value-changed', self.on_scroll_or_resize)
        self.next_button.connect('clicked', self.on_next_button_clicked)
        self.prev_button.connect('clicked', self.on_prev_button_clicked)

    def add_content_widget(self, name, widget):
        self.content_vbox.append(widget)
        self.content_vbox_children.append(widget)

    def add_label(self, name, text):
        label_inline = Gtk.Label.new(text)
        label_inline.set_xalign(0)
        label_inline.get_style_context().add_class('headline')
        self.content_vbox.append(label_inline)
        self.content_vbox_children.append(label_inline)

        label_overlay = Gtk.Label.new(text)
        label_overlay.set_xalign(0)
        label_overlay.set_halign(Gtk.Align.START)
        label_overlay.set_valign(Gtk.Align.START)
        label_overlay.set_size_request(148, -1)
        label_overlay.get_style_context().add_class('overlay')
        label_overlay.set_can_target(False)
        self.add_overlay(label_overlay)

        self.labels[name] = {'inline': label_inline, 'overlay': label_overlay}

    def add_buttons(self):
        self.tabs = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        self.prev_button = Gtk.Button()
        self.prev_button.set_icon_name('go-up-symbolic')
        self.prev_button.set_tooltip_text(_('Back'))
        self.prev_button.get_style_context().add_class('flat')
        self.prev_button.set_can_focus(False)
        self.tabs.append(self.prev_button)

        self.next_button = Gtk.Button()
        self.next_button.set_icon_name('go-down-symbolic')
        self.next_button.set_tooltip_text(_('Forward'))
        self.next_button.get_style_context().add_class('flat')
        self.next_button.set_can_focus(False)
        self.tabs.append(self.next_button)

        self.tabs_box = Gtk.CenterBox()
        self.tabs_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.tabs_box.get_style_context().add_class('tabs-box')
        self.tabs_box.set_start_widget(Gtk.Label.new('Files'))
        self.tabs_box.set_end_widget(self.tabs)
        self.vbox.append(self.tabs_box)

    def on_scroll_or_resize(self, *args):
        scrolling_offset = self.scrolled_window.get_vadjustment().get_value()
        if scrolling_offset == 0:
            self.prev_button.set_sensitive(False)
        else:
            self.prev_button.set_sensitive(True)

        label_offsets = self.get_label_offsets()
        height_condition = scrolling_offset < self.content_vbox.get_allocated_height() - self.scrolled_window.get_allocated_height()
        label_condition = len(label_offsets) > 0 and scrolling_offset < label_offsets[-1]
        self.next_button.set_sensitive(height_condition and label_condition)

        self.update_labels()

    def update_labels(self):
        tabs_height = self.tabs_box.get_allocated_height()
        scrolling_offset = self.scrolled_window.get_vadjustment().get_value()

        if self.content_vbox.get_allocated_height() == self.scrolled_window.get_allocated_height():
            for label_name in self.labels:
                self.labels[label_name]['overlay'].set_visible(False)
        else:
            self.tabs_box.get_style_context().remove_class('no-border')
            for label_name, label_offset in zip(self.labels, self.get_label_offsets()):
                margin_top = max(0, label_offset - int(scrolling_offset))
                self.labels[label_name]['overlay'].set_visible(True)
                self.labels[label_name]['overlay'].set_margin_top(margin_top)

                if margin_top > 0 and margin_top <= tabs_height:
                    self.tabs_box.get_style_context().add_class('no-border')

    def on_next_button_clicked(self, button):
        scrolling_offset = self.scrolled_window.get_vadjustment().get_value()

        for label_offset in self.get_label_offsets():
            if scrolling_offset < label_offset:
                self.scroll_view(label_offset)
                break

    def on_prev_button_clicked(self, button):
        scrolling_offset = self.scrolled_window.get_vadjustment().get_value()

        for label_offset in reversed([0] + self.get_label_offsets()):
            if scrolling_offset > label_offset:
                self.scroll_view(label_offset)
                break

    def get_label_offsets(self):
        offsets = list()
        offset = self.tabs_box.get_allocated_height()
        labels = [label['inline'] for label in self.labels.values()]

        for child in self.content_vbox_children:
            if child in labels:
                offsets.append(offset)
            if child.is_visible():
                offset += child.get_allocated_height()
        return offsets

    def scroll_view(self, position, duration=0.2):
        adjustment = self.scrolled_window.get_vadjustment()
        self.scroll_to = {'position_start': adjustment.get_value(), 'position_end': position, 'time_start': time.time(), 'duration': duration}
        self.scrolled_window.set_kinetic_scrolling(False)
        GObject.timeout_add(15, self.do_scroll)

    def do_scroll(self):
        if self.scroll_to != None:
            adjustment = self.scrolled_window.get_vadjustment()
            time_elapsed = time.time() - self.scroll_to['time_start']
            if self.scroll_to['duration'] == 0:
                time_elapsed_percent = 1
            else:
                time_elapsed_percent = time_elapsed / self.scroll_to['duration']
            if time_elapsed_percent >= 1:
                adjustment.set_value(self.scroll_to['position_end'])
                self.scroll_to = None
                self.scrolled_window.set_kinetic_scrolling(True)
                return False
            else:
                adjustment.set_value(self.scroll_to['position_start'] * (1 - self.ease(time_elapsed_percent)) + self.scroll_to['position_end'] * self.ease(time_elapsed_percent))
                return True
        return False

    def ease(self, time): return (time - 1)**3 + 1


