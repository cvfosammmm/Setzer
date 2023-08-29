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
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo

from setzer.app.color_manager import ColorManager


class AutocompleteWidgetView(Gtk.DrawingArea):

    def __init__(self, model):
        Gtk.DrawingArea.__init__(self)

        self.model = model

        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)

        self.layout = Pango.Layout(self.model.source_view.get_pango_context())

    def draw(self, drawing_area, ctx, width, height):
        si = self.model.model.selected_item_index
        fi = self.model.model.first_item_index

        if self.model.model.current_word == None or si == None: return

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('ac_bg'))
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('ac_selection_bg'))
        ctx.rectangle(0, self.model.line_height * (si - fi), width, self.model.line_height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('ac_text'))
        for i, item in enumerate(self.model.model.items[fi:fi + 5]):
            ctx.move_to(0, i * self.model.line_height)
            self.draw_item(ctx, item)

    def draw_item(self, ctx, item):
        offset = len(self.model.model.current_word)
        command_text = '<b>' + GLib.markup_escape_text(item['command'][:offset]) + '</b>'
        command_text += GLib.markup_escape_text(item['command'][offset:])

        self.dotlabels = filter(None, item['dotlabels'].split('###'))
        for dotlabel in self.dotlabels:
            command_text = command_text.replace('•', '<span alpha="60%">' + GLib.markup_escape_text(dotlabel) + '</span>', 1)

        self.layout.set_markup(command_text)
        PangoCairo.show_layout(ctx, self.layout)


