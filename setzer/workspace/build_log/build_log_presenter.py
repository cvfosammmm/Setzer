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
from gi.repository import cairo
from gi.repository import Pango

import os.path

import setzer.workspace.build_log.build_log_viewgtk as build_log_view
import setzer.helpers.drawing as drawing_helper
from setzer.helpers.timer import timer


class BuildLogPresenter(object):
    ''' Mediator between build log and view. '''
    
    def __init__(self, build_log, build_log_view):
        self.build_log = build_log
        self.view = build_log_view

        self.set_header_data(0, 0, False)
        self.view.list.connect('draw', self.draw)

        self.build_log.connect('build_log_finished_adding', self.on_build_log_finished_adding)
        self.build_log.connect('hover_item_changed', self.on_hover_item_changed)

        self.max_width = -1
        self.height = -1

    def on_build_log_finished_adding(self, build_log, has_been_built):
        num_errors = self.build_log.count_items('errors')
        num_others = self.build_log.count_items('warnings') + self.build_log.count_items('badboxes')
        num_items = self.build_log.count_items('all')
        self.set_header_data(num_errors, num_others, has_been_built)
        self.max_width = -1
        self.height = num_items * self.view.line_height + 6
        self.view.list.set_size_request(self.max_width, self.height)
        self.view.scrolled_window.get_vadjustment().set_value(0)
        self.view.scrolled_window.get_hadjustment().set_value(0)
        self.view.list.queue_draw()

    def on_hover_item_changed(self, build_log):
        self.view.list.queue_draw()

    #@timer
    def draw(self, drawing_area, ctx):
        update_size = False

        style_context = drawing_area.get_style_context()

        ctx.set_font_size(self.view.font_size)
        ctx.select_font_face(self.view.font.get_family(), cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL)

        offset = self.view.scrolled_window.get_vadjustment().get_value()
        view_width = self.view.scrolled_window.get_allocated_width()
        view_height = self.view.scrolled_window.get_allocated_height()
        additional_height = ctx.get_target().get_height() - view_height
        additional_lines = additional_height // self.view.line_height + 2

        bg_color = style_context.lookup_color('theme_base_color')[1]
        hover_color = self.view.list_color_hack_row.get_style_context().get_background_color(Gtk.StateFlags.PRELIGHT)
        fg_color = self.view.list_color_hack.get_style_context().get_color(style_context.get_state())

        ctx.set_source_rgba(bg_color.red, bg_color.green, bg_color.blue, bg_color.alpha)
        ctx.rectangle(0, max(0, offset - additional_height), view_width, max(len(self.build_log.items) * self.view.line_height, view_height + 2 * additional_height))
        ctx.fill()

        first_line = max(int(offset // self.view.line_height) - additional_lines, 0)
        last_line = min(int((offset + view_height) // self.view.line_height) + additional_lines, len(self.build_log.items))
        items = self.build_log.items[first_line:last_line]

        count = first_line
        ctx.set_source_rgba(fg_color.red, fg_color.green, fg_color.blue, fg_color.alpha)
        glyphs = list()
        for item in items:
            if count == self.build_log.hover_item:
                ctx.set_source_rgba(hover_color.red, hover_color.green, hover_color.blue, hover_color.alpha)
                ctx.rectangle(0, count * self.view.line_height, view_width, self.view.line_height)
                ctx.fill()

            surface = self.view.icons[item[0]]
            surface.set_device_offset(-12 * self.view.get_scale_factor(), -(count * self.view.line_height + 4) * self.view.get_scale_factor())
            ctx.set_source_surface(surface)
            ctx.rectangle(12, count * self.view.line_height + 4, 16, 16)
            ctx.fill()

            ctx.set_source_rgba(fg_color.red, fg_color.green, fg_color.blue, fg_color.alpha)

            ctx.move_to(40, (count + 1) * self.view.line_height - 7)
            ctx.show_text(item[0])

            ctx.move_to(116, (count + 1) * self.view.line_height - 7)
            text = drawing_helper.ellipsize_front(ctx, os.path.basename(item[2]), 120)
            ctx.show_text(text)

            ctx.move_to(254, (count + 1) * self.view.line_height - 7)
            ctx.show_text(_('Line {number}').format(number=str(item[3])) if item[3] >= 0 else '')

            ctx.move_to(330, (count + 1) * self.view.line_height - 7)
            ctx.show_text(item[4])
            count += 1

            if (342 + ctx.text_extents(item[4]).width) > self.max_width:
                self.max_width = (342 + ctx.text_extents(item[4]).width)
                update_size = True

        if update_size:
            drawing_area.set_size_request(self.max_width, self.height)

    def set_header_data(self, errors, warnings, tried_building=False):
        if tried_building:
            if self.build_log.document.build_system.build_time != None:
                time_string = '{:.2f}s, '.format(self.build_log.document.build_system.build_time)
            else:
                time_string = ''

            str_errors = ngettext('Building failed with {amount} error', 'Building failed with {amount} errors', errors)
            str_warnings = ngettext('{amount} warning or badbox', '{amount} warnings or badboxes', warnings)

            if errors == 0:
                markup = '<b>' + _('Building successful') + '</b> (' + time_string
            else:
                markup = '<b>' + str_errors.format(amount=str(errors)) + '</b> ('

            if warnings == 0:
                markup += _('no warnings or badboxes') 
            else:
                markup += str_warnings.format(amount=str(warnings))

            markup += ').'
            self.view.header_label.set_markup(markup)
        else:
            self.view.header_label.set_markup('')
    

