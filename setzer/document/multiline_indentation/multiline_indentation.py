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

from setzer.app.service_locator import ServiceLocator
from setzer.app.font_manager import FontManager


class MultilineIndentation(object):

    def __init__(self, document):
        self.document = document
        self.source_buffer = self.document.source_buffer
        self.adjustment = self.document.view.scrolled_window.get_vadjustment()

        self.char_width = FontManager.get_char_width(self.document.view.source_view, ' ')
        self.indentation_update = None
        self.indentation_tags = dict()

        self.document.parser.connect('finished_parsing', self.on_parser_update)
        self.document.connect('changed', self.on_document_changed)
        self.source_buffer.connect('notify::cursor-position', self.on_cursor_position_change)
        self.adjustment.connect('changed', self.on_adjustment_change)
        self.adjustment.connect('value-changed', self.on_adjustment_value_change)

    def on_parser_update(self, parser):
        if parser.last_edit[0] == 'insert':
            _, location_iter, text, text_length = parser.last_edit
            self.indentation_update = {'line_start': location_iter.get_line(), 'text_length': text_length}
        elif parser.last_edit[0] == 'delete':
            _, start_iter, end_iter = parser.last_edit
            self.indentation_update = {'line_start': start_iter.get_line(), 'text_length': 0}

    def on_document_changed(self, document):
        if self.indentation_update != None:
            _, start_iter = self.source_buffer.get_iter_at_line(self.indentation_update['line_start'])
            end_iter = start_iter.copy()
            end_iter.forward_chars(self.indentation_update['text_length'])
            end_iter.forward_to_line_end()
            start_iter.set_line_offset(0)
            text = self.source_buffer.get_text(start_iter, end_iter, True)
            for count, line in enumerate(text.splitlines()):
                for tag in start_iter.get_tags():
                    self.source_buffer.remove_tag(tag, start_iter, end_iter)
                number_of_characters = len(line.replace('\t', ' ' * ServiceLocator.get_settings().get_value('preferences', 'tab_width'))) - len(line.lstrip())
                if number_of_characters > 0:
                    end_iter = start_iter.copy()
                    end_iter.forward_chars(1)
                    self.source_buffer.apply_tag(self.get_indentation_tag(number_of_characters), start_iter, end_iter)
                start_iter.forward_line()

            self.indentation_update = None
        self.update_tags()

    def on_cursor_position_change(self, buffer, position):
        self.update_tags()

    def on_adjustment_change(self, adjustment):
        self.update_tags()

    def on_adjustment_value_change(self, adjustment):
        self.update_tags()

    def update_tags(self):
        char_width = FontManager.get_char_width(self.document.view.source_view, ' ')
        if char_width != self.char_width:
            self.char_width = char_width
            for number_of_characters, tag in self.indentation_tags.items():
                tag.set_property('indent', -1 * number_of_characters * self.char_width)

    def get_indentation_tag(self, number_of_characters):
        try:
            tag = self.indentation_tags[number_of_characters]
        except KeyError:
            tag = self.source_buffer.create_tag('indentation-' + str(number_of_characters))
            tag.set_property('indent', -1 * number_of_characters * self.char_width)
            self.indentation_tags[number_of_characters] = tag
        return tag


