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
from gi.repository import Pango
from gi.repository import PangoCairo

import os.path
import cairo

import setzer.workspace.build_log.build_log_viewgtk as build_log_view
import setzer.helpers.drawing as drawing_helper
from setzer.helpers.timer import timer


class BuildLogPresenter(object):
    ''' Mediator between build log and view. '''
    
    def __init__(self, build_log, build_log_view):
        self.build_log = build_log
        self.view = build_log_view

        self.line_cache = dict()

        self.set_header_data(0, 0, False)
        self.view.list.connect('draw', self.draw)

        self.build_log.connect('build_log_finished_adding', self.on_build_log_finished_adding)
        self.build_log.connect('hover_item_changed', self.on_hover_item_changed)

        self.max_width = -1
        self.height = -1

    def on_build_log_finished_adding(self, build_log, has_been_built):
        self.line_cache = dict()
        num_errors = self.build_log.count_items('errors')
        num_others = self.build_log.count_items('warnings') + self.build_log.count_items('badboxes')
        num_items = self.build_log.count_items('all')
        self.set_header_data(num_errors, num_others, has_been_built)
        self.max_width = -1
        self.height = num_items * self.view.line_height + 24
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

        offset = self.view.scrolled_window.get_vadjustment().get_value()
        view_width = drawing_area.get_allocated_width()
        view_height = self.view.scrolled_window.get_allocated_height()
        additional_height = ctx.get_target().get_height() - view_height
        additional_lines = additional_height // self.view.line_height + 2

        bg_color = style_context.lookup_color('theme_base_color')[1]
        hover_color = style_context.lookup_color('theme_bg_color')[1]
        self.view.fg_color = style_context.lookup_color('theme_fg_color')[1]

        ctx.set_source_rgba(bg_color.red, bg_color.green, bg_color.blue, bg_color.alpha)
        ctx.rectangle(0, max(0, offset - additional_height), view_width, max(len(self.build_log.items) * self.view.line_height, view_height + 2 * additional_height))
        ctx.fill()

        first_line = max(int(offset // self.view.line_height) - additional_lines, 0)
        last_line = min(int((offset + view_height) // self.view.line_height) + additional_lines, len(self.build_log.items))
        items = self.build_log.items[first_line:last_line]

        count = first_line
        ctx.set_source_rgba(self.view.fg_color.red, self.view.fg_color.green, self.view.fg_color.blue, self.view.fg_color.alpha)
        for item in items:
            if count == self.build_log.hover_item:
                ctx.set_source_rgba(hover_color.red, hover_color.green, hover_color.blue, hover_color.alpha)
                ctx.rectangle(0, count * self.view.line_height - 1, view_width, self.view.line_height - 1)
                ctx.fill()

            self.draw_line(ctx, item, count)
            count += 1

            if (342 + self.view.layout.get_extents()[1].width / Pango.SCALE) > self.max_width:
                self.max_width = 342 + self.view.layout.get_extents()[1].width / Pango.SCALE
                update_size = True

        if update_size:
            drawing_area.set_size_request(self.max_width, self.height)

    def draw_line(self, da_context, item, count):
        if count not in self.line_cache:
            surface = cairo.ImageSurface(cairo.Format.ARGB32, 350 + len(item[4]) * self.view.line_height, self.view.line_height)
            ctx = cairo.Context(surface)

            icon_surface = self.view.icons[item[0]]
            ctx.set_source_surface(icon_surface)
            ctx.rectangle(0, 1, 16, 16)
            ctx.fill()

            ctx.set_source_rgba(self.view.fg_color.red, self.view.fg_color.green, self.view.fg_color.blue, self.view.fg_color.alpha)

            ctx.move_to(40, -1)
            self.view.layout.set_text(item[0])
            PangoCairo.show_layout(ctx, self.view.layout)

            ctx.move_to(116, -1)
            self.view.layout.set_width(120 * Pango.SCALE)
            self.view.layout.set_text(item[2])
            PangoCairo.show_layout(ctx, self.view.layout)
            self.view.layout.set_width(-1)

            ctx.move_to(254, -1)
            self.view.layout.set_text(_('Line {number}').format(number=str(item[3])) if item[3] >= 0 else '')
            PangoCairo.show_layout(ctx, self.view.layout)

            ctx.move_to(330, -1)
            self.view.layout.set_text(item[4])
            PangoCairo.show_layout(ctx, self.view.layout)

            self.line_cache[count] = surface

        surface = self.line_cache[count]
        surface.set_device_offset(-12 * self.view.get_scale_factor(), -(count * self.view.line_height + 3) * self.view.get_scale_factor())
        da_context.set_source_surface(surface)
        da_context.rectangle(12, count * self.view.line_height + 4, 350 + len(item[4]) * self.view.line_height, self.view.line_height)
        da_context.fill()

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
    

