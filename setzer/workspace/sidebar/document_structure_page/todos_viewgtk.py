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
from gi.repository import Gtk, Gdk, Pango, Graphene

import setzer.workspace.sidebar.document_structure_page.structure_widget as structure_widget
from setzer.app.service_locator import ServiceLocator


class TodosSectionView(structure_widget.StructureWidget):

    def __init__(self, model):
        structure_widget.StructureWidget.__init__(self, model)

        self.layout = Pango.Layout(self.get_pango_context())
        self.layout.set_font_description(self.font)
        self.layout.set_spacing(8 * Pango.SCALE)
        self.layout.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout.set_text('\n')

        self.line_height = int(self.layout.get_extents()[0].height / Pango.SCALE)

    def do_snapshot(self, snapshot):
        self.drawing_setup()
        self.setup_icons()
        self.draw_background(snapshot)
        self.draw_hover_background(snapshot, len(self.model.todos))

        snapshot.translate(Graphene.Point().init(9, 13))

        text = ''
        for count, label in enumerate(self.model.todos):
            text += label[0] + '\n'

        self.layout.set_text(text)
        self.layout.set_width((self.get_allocated_width() - 47) * Pango.SCALE)
        snapshot.translate(Graphene.Point().init(26, -1))
        snapshot.append_layout(self.layout, self.fg_color)
        snapshot.translate(Graphene.Point().init(-26, 1))

        for count, label in enumerate(self.model.todos):
            self.icons['starred-symbolic'].snapshot_symbolic(snapshot, 16, 16, [self.fg_color])
            snapshot.translate(Graphene.Point().init(0, self.line_height))

    def setup_icons(self, widget=None):
        icon_theme = Gtk.IconTheme.get_for_display(ServiceLocator.get_main_window().get_display())
        icon = icon_theme.lookup_icon('starred-symbolic', None, 16, self.get_scale_factor(), Gtk.TextDirection.LTR, 0)
        self.icons['starred-symbolic'] = icon


