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
from gi.repository import Gtk, Pango, Graphene, Gsk

import re
import os.path

from setzer.app.service_locator import ServiceLocator
from setzer.app.color_manager import ColorManager
from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.helpers.popover import Popover


class DocumentSwitcherView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(414)

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.get_style_context().add_class('documentswitcher')

        self.root_explaination1 = Gtk.Label.new(_('Click on a document in the list below to set it as root.'))
        self.root_explaination1.set_margin_top(6)
        self.root_explaination1.set_xalign(0)
        self.root_explaination1.get_style_context().add_class('explaination-header')
        self.root_explaination2 = Gtk.Label.new(_('The root document will get built, no matter which document\nyou are currently editing, and it will always display in the .pdf\npreview. The build log will also refer to the root document.\nThis is often useful for working on large projects where typically\na top level document (the root) will contain multiple lower\nlevel files via include statements.'))
        self.root_explaination2.set_xalign(0)
        self.root_explaination2.get_style_context().add_class('explaination')
        self.root_explaination2.set_margin_top(15)
        self.root_explaination2.set_margin_bottom(10)
        self.root_explaination_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.root_explaination_box.append(self.root_explaination1)
        self.root_explaination_box.append(self.root_explaination2)
        self.root_explaination_revealer = Gtk.Revealer()
        self.root_explaination_revealer.set_child(self.root_explaination_box)
        self.root_explaination_revealer.set_reveal_child(False)

        self.document_list = DocumentChooserList()

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.document_list)
        self.scrolled_window.set_min_content_height(self.document_list.line_height + 24)
        self.scrolled_window.set_min_content_width(398)
        self.scrolled_window.set_max_content_height(18 * self.document_list.line_height - 15)
        self.scrolled_window.set_max_content_width(398)
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_propagate_natural_width(True)

        self.set_root_document_button = MenuBuilder.create_button(_('Set one Document as Root'))
        self.set_root_document_button.set_can_focus(False)
        self.unset_root_document_button = MenuBuilder.create_button(_('Unset Root Document'))
        self.unset_root_document_button.set_can_focus(False)

        self.box.append(self.root_explaination_revealer)
        self.box.append(self.scrolled_window)
        self.box.append(self.set_root_document_button)
        self.box.append(self.unset_root_document_button)
        self.add_widget(self.box)


class DocumentChooserList(Gtk.Widget):
    
    def __init__(self):
        Gtk.Widget.__init__(self)

        self.items = []
        self.visible_items = []
        self.pointer_x = None
        self.pointer_y = None
        self.selected_index = None
        self.close_button_active = False
        self.button_pressed = False
        self.root_selection_mode = False

        self.font = self.get_pango_context().get_font_description()
        self.font_size = self.font.get_size() / Pango.SCALE

        self.layout_header = Pango.Layout(self.get_pango_context())
        self.layout_header.set_ellipsize(Pango.EllipsizeMode.START)
        self.layout_header.set_width(374 * Pango.SCALE)
        self.layout_header.set_font_description(self.font)
        self.layout_header.set_text('\n')

        icon_theme = Gtk.IconTheme.get_for_display(ServiceLocator.get_main_window().get_display())
        self.icons = dict()
        self.icons['latex'] = icon_theme.lookup_icon('document-latex-symbolic', None, 16, self.get_scale_factor(), Gtk.TextDirection.LTR, 0)
        self.icons['bibtex'] = icon_theme.lookup_icon('document-bibtex-symbolic', None, 16, self.get_scale_factor(), Gtk.TextDirection.LTR, 0)
        self.icons['other'] = icon_theme.lookup_icon('document-other-symbolic', None, 16, self.get_scale_factor(), Gtk.TextDirection.LTR, 0)
        self.icons['root'] = icon_theme.lookup_icon('emblem-ok-symbolic', None, 16, self.get_scale_factor(), Gtk.TextDirection.LTR, 0)
        self.icons['close'] = icon_theme.lookup_icon('window-close-symbolic', None, 16, self.get_scale_factor(), Gtk.TextDirection.LTR, 0)

        self.line_height = int(self.layout_header.get_extents()[0].height / Pango.SCALE)
        self.layout_header.set_spacing((self.line_height - 4) * Pango.SCALE)

    def do_snapshot(self, snapshot):
        fg_color = ColorManager.get_ui_color('window_fg_color')
        fg_color_light = ColorManager.get_ui_color('fg_color_light')
        bg_color = ColorManager.get_ui_color('popover_bg_color')
        active_color = ColorManager.get_ui_color('view_hover_color')
        root_color_string = ColorManager.get_ui_color_string_with_alpha('fg_color_light')
        iheight = (15 + self.line_height)
        hover_item = self.get_hover_item()

        snapshot.append_color(bg_color, Graphene.Rect().init(0, 0, self.get_allocated_width(), self.get_allocated_height()))

        if hover_item != None or self.selected_index != None:
            if self.selected_index != None:
                rect = Graphene.Rect().init(0, self.selected_index * iheight, self.get_allocated_width(), iheight)
            elif hover_item != None:
                rect = Graphene.Rect().init(0, hover_item * iheight, self.get_allocated_width(), iheight)
            rounded_rect = Gsk.RoundedRect()
            rounded_rect.init_from_rect(rect, radius=6)
            snapshot.push_rounded_clip(rounded_rect)
            snapshot.append_color(active_color, rect)
            snapshot.pop()

        snapshot.translate(Graphene.Point().init(9, 9))
        for i, document in enumerate(self.visible_items):
            modified_suffix = ('*' if document.source_buffer.get_modified() else '')
            root_suffix = ('  <span color="' + root_color_string + '">(root)</span>' if document.get_is_root() else '')
            filename_text = os.path.split(document.get_displayname())[1] + modified_suffix + root_suffix + '\n'
            snapshot.translate(Graphene.Point().init(23, -1))
            self.layout_header.set_markup(filename_text)
            snapshot.append_layout(self.layout_header, fg_color)
            snapshot.translate(Graphene.Point().init(-23, 1))

            if self.root_selection_mode:
                if i == hover_item:
                    self.icons['root'].snapshot_symbolic(snapshot, 16, 16, [fg_color])
                snapshot.translate(Graphene.Point().init(0, self.line_height + 15))
            else:
                if document.get_is_root():
                    self.icons['root'].snapshot_symbolic(snapshot, 16, 16, [fg_color])
                else:
                    self.icons[document.get_document_type()].snapshot_symbolic(snapshot, 16, 16, [fg_color])
                snapshot.translate(Graphene.Point().init(self.get_allocated_width() - 34, 0))

                if i == hover_item and self.pointer_x > self.get_allocated_width() - 34:
                    snapshot.translate(Graphene.Point().init(- 4, - 4))
                    rect = Graphene.Rect().init(0, 0, 24, iheight - 10)
                    rounded_rect = Gsk.RoundedRect()
                    rounded_rect.init_from_rect(rect, radius=6)
                    snapshot.push_rounded_clip(rounded_rect)
                    snapshot.append_color(active_color, rect)
                    snapshot.pop()

                    snapshot.translate(Graphene.Point().init(4, 4))
                    self.icons['close'].snapshot_symbolic(snapshot, 16, 16, [fg_color])
                else:
                    self.icons['close'].snapshot_symbolic(snapshot, 16, 16, [fg_color_light])

                snapshot.translate(Graphene.Point().init(34 - self.get_allocated_width(), self.line_height + 15))

    def get_hover_item(self):
        if self.pointer_y == None:
            return None
        else:
            item_num = int((self.pointer_y) // (15 + self.line_height))
            if item_num < 0 or item_num > (len(self.visible_items) - 1):
                return None
            else:
                return item_num

    def update_items(self):
        if self.root_selection_mode:
            self.visible_items = [document for document in self.items if document.is_latex_document()]
        else:
            self.visible_items = self.items
        self.set_size_request(386, len(self.visible_items) * (self.line_height + 15) + 6)
        self.visible_items.sort(key=lambda val: -val.get_last_activated())
        self.queue_draw()


