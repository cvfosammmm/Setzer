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
from gi.repository import Gtk
from gi.repository import Graphene
from gi.repository import Pango

from setzer.app.service_locator import ServiceLocator
from setzer.app.color_manager import ColorManager
from setzer.helpers.timer import timer
import setzer.helpers.drawing as drawing_helper

import os.path


class BuildLogView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('buildlog')

        self.list = BuildLogList(self)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_child(self.list)

        self.close_button = Gtk.Button.new_from_icon_name('window-close-symbolic')
        self.close_button.get_style_context().add_class('flat')
        self.close_button.set_can_focus(False)
        self.close_button.set_action_name('win.close-build-log')

        self.header_label = Gtk.Label()
        self.header_label.set_size_request(300, -1)
        self.header_label.set_xalign(0)
        self.header_label.set_margin_start(0)
        self.header_label.set_hexpand(True)        

        self.header = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.header.append(self.header_label)
        self.header.append(self.close_button)

        self.append(self.header)
        self.append(self.scrolled_window)
        self.set_size_request(200, 200)


class BuildLogList(Gtk.Widget):

    def __init__(self, parent):
        Gtk.Widget.__init__(self)
        self.parent = parent
        self.icons = list()

        self.items = []
        self.hover_item = None
        self.offset_start = 0
        self.offset_end = 0

        self.font = self.get_pango_context().get_font_description()
        self.font_size = self.font.get_size() / Pango.SCALE

        self.layouts = list()
        for i in range(4):
            layout = Pango.Layout(self.get_pango_context())
            layout.set_font_description(self.font)
            layout.set_spacing(8 * Pango.SCALE)
            layout.set_text('\n')
            self.layouts.append(layout)

        self.line_height = self.layouts[0].get_extents()[0].height / Pango.SCALE

    def do_snapshot(self, snapshot):
        self.offset_start = self.parent.scrolled_window.get_vadjustment().get_value()
        self.offset_end = self.offset_start + self.parent.scrolled_window.get_vadjustment().get_page_size()

        self.setup_icons()

        fg_color = ColorManager.get_ui_color('view_fg_color')
        bg_color = ColorManager.get_ui_color('view_bg_color')
        hover_color = ColorManager.get_ui_color('view_hover_color')

        snapshot.append_color(bg_color, Graphene.Rect().init(0, self.offset_start, self.get_allocated_width(), self.offset_end + 2000))
        if self.hover_item != None:
            snapshot.append_color(hover_color, Graphene.Rect().init(0, self.hover_item * self.line_height, self.get_allocated_width(), self.line_height))

        snapshot.translate(Graphene.Point().init(40, 3))
        snapshot.append_layout(self.layouts[0], fg_color)
        snapshot.translate(Graphene.Point().init(76, 0))
        snapshot.append_layout(self.layouts[1], fg_color)
        snapshot.translate(Graphene.Point().init(138, 0))
        snapshot.append_layout(self.layouts[2], fg_color)
        snapshot.translate(Graphene.Point().init(76, 0))
        snapshot.append_layout(self.layouts[3], fg_color)

        snapshot.translate(Graphene.Point().init(- (40 + 76 + 138 + 76), 0))
        snapshot.translate(Graphene.Point().init(12, 2))
        for i, item in enumerate(self.items):
            self.icons[item[0]].snapshot_symbolic(snapshot, 16, 16, [fg_color])
            snapshot.translate(Graphene.Point().init(0, self.line_height))

    def generate_layouts(self):
        first_item = min(max(int(self.offset_start // self.line_height) - 5, 0), len(self.items))
        last_item = min(int(self.offset_end // self.line_height) + 7, len(self.items))

        type_text = ''
        file_text = ''
        line_text = ''
        desc_text = ''
        for i, item in enumerate(self.items):
            type_text += item[0] + '\n'
            file_text += os.path.basename(item[2]) + '\n'
            line_text += _('Line {number}').format(number=str(item[3])) + "\n" if item[3] >= 0 else '' + '\n'
            desc_text += item[4] + '\n'

        self.layouts[0].set_text(type_text)
        self.layouts[0].set_width(70 * Pango.SCALE)

        self.layouts[1].set_text(file_text)
        self.layouts[1].set_ellipsize(Pango.EllipsizeMode.START)
        self.layouts[1].set_width(132 * Pango.SCALE)

        self.layouts[2].set_text(line_text)
        self.layouts[2].set_ellipsize(Pango.EllipsizeMode.NONE)
        self.layouts[2].set_width(70 * Pango.SCALE)

        self.layouts[3].set_text(desc_text)
        self.layouts[3].set_width(-1)

    def setup_icons(self, widget=None):
        icon_theme = Gtk.IconTheme.get_for_display(ServiceLocator.get_main_window().get_display())

        self.icons = dict()
        for icon_type, icon_name in [('Error', 'dialog-error-symbolic'), ('Warning', 'dialog-warning-symbolic'), ('Badbox', 'own-badbox-symbolic')]:
            icon = icon_theme.lookup_icon(icon_name, None, 16, self.get_scale_factor(), Gtk.TextDirection.LTR, 0)
            self.icons[icon_type] = icon


