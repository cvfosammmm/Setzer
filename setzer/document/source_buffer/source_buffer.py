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
gi.require_version('GtkSource', '4')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GtkSource
from gi.repository import Pango

import os.path
import re
import time
import math
import difflib

from setzer.app.service_locator import ServiceLocator
import setzer.helpers.timer as timer


class SourceBuffer(GtkSource.Buffer):

    def __init__(self, document):
        GtkSource.Buffer.__init__(self)

        self.document = document
        self.view = GtkSource.View.new_with_buffer(self)
        self.view.set_monospace(True)
        self.view.set_smart_home_end(True)
        self.view.set_auto_indent(True)
        self.view.set_left_margin(6)
        self.settings = ServiceLocator.get_settings()

        resources_path = ServiceLocator.get_resources_path()

        self.mover_mark = self.create_mark('mover', self.get_start_iter(), True)

        # set source language for syntax highlighting
        self.source_language_manager = GtkSource.LanguageManager()
        self.source_language = self.source_language_manager.get_language(self.document.get_gsv_language_name())
        self.set_language(self.source_language)

        self.source_style_scheme_manager = GtkSource.StyleSchemeManager()
        self.source_style_scheme_manager.set_search_path((os.path.join(resources_path, 'gtksourceview', 'styles'),))
        self.source_style_scheme_light = self.source_style_scheme_manager.get_scheme('setzer')
        self.source_style_scheme_dark = self.source_style_scheme_manager.get_scheme('setzer-dark')

        self.search_settings = GtkSource.SearchSettings()
        self.search_context = GtkSource.SearchContext.new(self, self.search_settings)
        self.search_context.set_highlight(True)

        self.synctex_tag_count = 0
        self.synctex_highlight_tags = dict()

        self.document.add_change_code('buffer_ready')
        
    def insert_before_document_end(self, text):
        end_iter = self.get_end_iter()
        result = end_iter.backward_search('\\end{document}', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
        if result != None:
            self.insert_text_at_iter(result[0], '''
''' + text + '''

''', False)
        else:
            self.insert_text_at_cursor(text)

    def add_packages(self, packages):
        first_package = True
        text = ''
        for packagename in packages:
            if not first_package: text += '\n'
            text += '\\usepackage{' + packagename + '}'
            first_package = False
        
        end_iter = self.get_end_iter()
        result = end_iter.backward_search('\\usepackage', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
        if result != None:
            result[0].forward_to_line_end()
            self.insert_text_at_iter(result[0], '\n' + text)
        else:
            end_iter = self.get_end_iter()
            result = end_iter.backward_search('\\documentclass', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
            if result != None:
                result[0].forward_to_line_end()
                self.insert_text_at_iter(result[0], '\n' + text)
            else:
                self.insert_text_at_cursor(text)

    def remove_packages(self, packages):
        packages_dict = self.document.parser.symbols['packages_detailed']
        for package in packages:
            try:
                match_obj = packages_dict[package]
            except KeyError: return
            start_iter = self.get_iter_at_offset(match_obj.start())
            end_iter = self.get_iter_at_offset(match_obj.end())
            text = self.get_text(start_iter, end_iter, False)
            if text == match_obj.group(0):  
                if start_iter.get_line_offset() == 0:
                    start_iter.backward_char()
                self.delete(start_iter, end_iter)

    def insert_text(self, line_number, offset, text, indent_lines=True):
        insert_iter = self.get_iter_at_line_offset(line_number, offset)
        self.insert_text_at_iter(insert_iter, text, indent_lines)

    def insert_text_at_iter(self, insert_iter, text, indent_lines=True):
        self.place_cursor(insert_iter)
        self.insert_text_at_cursor(text, indent_lines)

    def insert_text_at_cursor(self, text, indent_lines=True, scroll=True, select_dot=True):
        self.begin_user_action()

        # replace tabs with spaces, if set in preferences
        if self.settings.get_value('preferences', 'spaces_instead_of_tabs'):
            number_of_spaces = self.settings.get_value('preferences', 'tab_width')
            text = text.replace('\t', ' ' * number_of_spaces)

        dotcount = text.count('•')
        insert_iter = self.get_iter_at_mark(self.get_insert())
        bounds = self.get_selection_bounds()
        selection = ''
        if dotcount == 1:
            bounds = self.get_selection_bounds()
            if len(bounds) > 0:
                selection = self.get_text(bounds[0], bounds[1], True)
                if len(selection) > 0:
                    text = text.replace('•', selection, 1)

        if indent_lines:
            line_iter = self.get_iter_at_line(insert_iter.get_line())
            ws_line = self.get_text(line_iter, insert_iter, False)
            lines = text.split('\n')
            ws_number = len(ws_line) - len(ws_line.lstrip())
            whitespace = ws_line[:ws_number]
            final_text = ''
            for no, line in enumerate(lines):
                if no != 0:
                    final_text += '\n' + whitespace
                final_text += line
        else:
            final_text = text

        self.delete_selection(False, False)
        self.insert_at_cursor(final_text)

        if select_dot:
            dotindex = final_text.find('•')
            if dotcount > 0:
                selection_len = len(selection) if dotcount == 1 else 0
                start = self.get_iter_at_mark(self.get_insert())
                start.backward_chars(abs(dotindex + selection_len - len(final_text)))
                self.place_cursor(start)
                end = start.copy()
                end.forward_char()
                self.select_range(start, end)

        if scroll:
            self.scroll_cursor_onscreen()

        self.end_user_action()

    def replace_range(self, start_iter, end_iter, text, indent_lines=True, select_dot=True):
        self.begin_user_action()

        if indent_lines:
            line_iter = self.get_iter_at_line(start_iter.get_line())
            ws_line = self.get_text(line_iter, start_iter, False)
            lines = text.split('\n')
            ws_number = len(ws_line) - len(ws_line.lstrip())
            whitespace = ws_line[:ws_number]
            final_text = ''
            for no, line in enumerate(lines):
                if no != 0:
                    final_text += '\n' + whitespace
                final_text += line
        else:
            final_text = text

        self.delete(start_iter, end_iter)
        self.insert(start_iter, final_text)

        if select_dot:
            dotindex = final_text.find('•')
            if dotindex > -1:
                start_iter.backward_chars(abs(dotindex - len(final_text)))
                bound = start_iter.copy()
                bound.forward_chars(1)
                self.select_range(start_iter, bound)

        self.end_user_action()

    def insert_before_after(self, before, after):
        bounds = self.get_selection_bounds()

        if len(bounds) > 1:
            text = before + self.get_text(*bounds, 0) + after
            self.replace_range(bounds[0], bounds[1], text)
        else:
            text = before + '•' + after
            self.insert_text_at_cursor(text)

    def comment_uncomment(self):
        self.begin_user_action()

        bounds = self.get_selection_bounds()

        if len(bounds) > 1:
            end = (bounds[1].get_line() + 1) if (bounds[1].get_line_index() > 0) else bounds[1].get_line()
            line_numbers = list(range(bounds[0].get_line(), end))
        else:
            line_numbers = [self.get_iter_at_mark(self.get_insert()).get_line()]

        do_comment = False
        for line_number in line_numbers:
            line = self.get_line(line_number)
            if not line.startswith('%'):
                do_comment = True

        if do_comment:
            for line_number in line_numbers:
                self.insert(self.get_iter_at_line(line_number), '%')
        else:
            for line_number in line_numbers:
                start = self.get_iter_at_line(line_number)
                end = start.copy()
                end.forward_char()
                self.delete(start, end)

        self.end_user_action()

    def get_line(self, line_number):
        start = self.get_iter_at_line(line_number)
        end = start.copy()
        if not end.ends_line():
            end.forward_to_line_end()
        return self.get_slice(start, end, False)

    def get_all_text(self):
        return self.get_text(self.get_start_iter(), self.get_end_iter(), True)

    def set_synctex_position(self, position):
        start = self.get_iter_at_line(position['line'])
        end = start.copy()
        if not start.ends_line():
            end.forward_to_line_end()
        text = self.get_text(start, end, False)

        matches = self.get_synctex_word_bounds(text, position['word'], position['context'])
        if matches != None:
            for word_bounds in matches:
                end = start.copy()
                new_start = start.copy()
                new_start.forward_chars(word_bounds[0])
                end.forward_chars(word_bounds[1])
                self.add_synctex_tag(new_start, end)
        else:
            ws_number = len(text) - len(text.lstrip())
            start.forward_chars(ws_number)
            self.add_synctex_tag(start, end)

    def add_synctex_tag(self, start_iter, end_iter):
        self.place_cursor(start_iter)
        self.synctex_tag_count += 1
        self.create_tag('synctex_highlight-' + str(self.synctex_tag_count), background_rgba=Gdk.RGBA(0.976, 0.941, 0.420, 0.6), background_full_height=True)
        tag = self.get_tag_table().lookup('synctex_highlight-' + str(self.synctex_tag_count))
        self.apply_tag(tag, start_iter, end_iter)
        if not self.synctex_highlight_tags:
            GObject.timeout_add(15, self.remove_or_color_synctex_tags)
        self.synctex_highlight_tags[self.synctex_tag_count] = {'tag': tag, 'time': time.time()}
        self.scroll_cursor_onscreen()

    def get_synctex_word_bounds(self, text, word, context):
        if not word: return None
        word = word.split(' ')
        if len(word) > 2:
            word = word[:2]
        word = ' '.join(word)
        regex_pattern = re.escape(word)

        for c in regex_pattern:
            if ord(c) > 127:
                regex_pattern = regex_pattern.replace(c, '(?:\w)')

        matches = list()
        top_score = 0.1
        regex = ServiceLocator.get_regex('(\W{0,1})' + regex_pattern.replace('\x1b', '(?:\w{2,3})').replace('\x1c', '(?:\w{2})').replace('\x1d', '(?:\w{2,3})').replace('\-', '(?:-{0,1})') + '(\W{0,1})')
        for match in regex.finditer(text):
            offset1 = context.find(word)
            offset2 = len(context) - offset1 - len(word)
            match_text = text[max(match.start() - max(offset1, 0), 0):min(match.end() + max(offset2, 0), len(text))]
            score = difflib.SequenceMatcher(None, match_text, context).ratio()
            if bool(match.group(1)) or bool(match.group(2)):
                if score > top_score + 0.1:
                    top_score = score
                    matches = [[match.start() + len(match.group(1)), match.end() - len(match.group(2))]]
                elif score > top_score - 0.1:
                    matches.append([match.start() + len(match.group(1)), match.end() - len(match.group(2))])
        if len(matches) > 0:
            return matches
        else:
            return None

    def remove_or_color_synctex_tags(self):
        for tag_count in list(self.synctex_highlight_tags):
            item = self.synctex_highlight_tags[tag_count]
            time_factor = time.time() - item['time']
            if time_factor > 1.5:
                if time_factor <= 1.75:
                    opacity_factor = self.ease(1 - (time_factor - 1.5) * 4)
                    item['tag'].set_property('background-rgba', Gdk.RGBA(0.976, 0.941, 0.420, opacity_factor * 0.6))
                else:
                    start = self.get_start_iter()
                    end = self.get_end_iter()
                    self.remove_tag(item['tag'], start, end)
                    self.get_tag_table().remove(item['tag'])
                    del(self.synctex_highlight_tags[tag_count])
        return bool(self.synctex_highlight_tags)

    def ease(self, factor): return (factor - 1)**3 + 1

    def place_cursor_and_scroll(self, line_number, offset=0):
        text_iter = self.get_iter_at_line_offset(line_number, offset)
        self.place_cursor(text_iter)
        self.scroll_cursor_onscreen()

    def scroll_cursor_onscreen(self):
        self.scroll_mark_onscreen(self.get_insert())

    def scroll_mark_onscreen(self, text_mark):
        self.scroll_iter_onscreen(self.get_iter_at_mark(text_mark))

    def scroll_iter_onscreen(self, text_iter):
        visible_lines = self.get_number_of_visible_lines()
        iter_position = self.view.get_iter_location(text_iter).y
        end_yrange = self.view.get_line_yrange(self.get_end_iter())
        buffer_height = end_yrange.y + end_yrange.height
        line_height = self.get_line_height()
        window_offset = self.view.get_visible_rect().y
        window_height = self.view.get_visible_rect().height
        gap = min(math.floor(max((visible_lines - 2), 0) / 2), 5)
        if iter_position < window_offset + gap * line_height:
            scroll_iter = self.view.get_iter_at_location(0, max(iter_position - gap * line_height, 0)).iter
            self.move_mark(self.mover_mark, scroll_iter)
            self.view.scroll_to_mark(self.mover_mark, 0, False, 0, 0)
        elif iter_position > (window_offset + window_height - (gap + 1) * line_height):
            scroll_iter = self.view.get_iter_at_location(0, min(iter_position + gap * line_height, buffer_height)).iter
            self.move_mark(self.mover_mark, scroll_iter)
            self.view.scroll_to_mark(self.mover_mark, 0, False, 0, 0)

    def get_number_of_visible_lines(self):
        line_height = self.get_line_height()
        return math.floor(self.view.get_visible_rect().height / line_height)

    def get_line_height(self):
        return self.view.get_iter_location(self.get_end_iter()).height

    def get_char_width(self):
        char_width, line_height = ServiceLocator.get_char_dimensions()
        return char_width

    def get_char_dimensions(self):
        context = self.view.get_pango_context()
        layout = Pango.Layout.new(context)
        layout.set_text(" ", -1)
        layout.set_font_description(context.get_font_description())
        return layout.get_pixel_size()

    def set_use_dark_scheme(self, use_dark_scheme):
        if use_dark_scheme: self.set_style_scheme(self.source_style_scheme_dark)
        else: self.set_style_scheme(self.source_style_scheme_light)


