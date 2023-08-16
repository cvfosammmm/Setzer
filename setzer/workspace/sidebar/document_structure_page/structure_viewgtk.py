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
from gi.repository import Gtk, Gdk, Graphene, Pango

import os.path

import setzer.workspace.sidebar.document_structure_page.structure_widget as structure_widget
from setzer.app.service_locator import ServiceLocator


class StructureSectionView(structure_widget.StructureWidget):

    def __init__(self, model):
        structure_widget.StructureWidget.__init__(self, model)

        self.layout = Pango.Layout(self.get_pango_context())
        self.layout.set_font_description(self.font)
        self.layout.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout.set_spacing(8 * Pango.SCALE)
        self.layout.set_text('\n')

        self.line_height = int(self.layout.get_extents()[0].height / Pango.SCALE)

    def do_snapshot(self, snapshot):
        self.drawing_setup()
        self.setup_icons()
        self.draw_background(snapshot)
        self.draw_hover_background(snapshot, len(self.model.nodes_in_line))

        snapshot.translate(Graphene.Point().init(9, 13))
        self.draw_nodes(self.model.nodes, 0, snapshot)

    def draw_nodes(self, nodes, level, snapshot):
        for node in nodes:
            if node['item'][2] == 'file-symbolic':
                text = os.path.basename(node['item'][3])
            else:
                text = node['item'][3]
            self.layout.set_text(text)
            self.layout.set_width((self.get_allocated_width() - 47 - 18 * level) * Pango.SCALE)

            snapshot.translate(Graphene.Point().init(26, -1))
            snapshot.append_layout(self.layout, self.fg_color)
            snapshot.translate(Graphene.Point().init(-26, 1))
            self.icons[node['item'][2]].snapshot_symbolic(snapshot, 16, 16, [self.fg_color])

            snapshot.translate(Graphene.Point().init(0, self.line_height))

            snapshot.translate(Graphene.Point().init(18, 0))
            self.draw_nodes(node['children'], level + 1, snapshot)
            snapshot.translate(Graphene.Point().init(-18, 0))

    def setup_icons(self, widget=None):
        icon_theme = Gtk.IconTheme.get_for_display(ServiceLocator.get_main_window().get_display())
        for icon_name in self.model.levels:
            icon = icon_theme.lookup_icon(icon_name + '-symbolic', None, 16, self.get_scale_factor(), Gtk.TextDirection.LTR, 0)
            self.icons[icon_name + '-symbolic'] = icon


