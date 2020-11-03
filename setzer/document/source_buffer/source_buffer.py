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
        self.settings = ServiceLocator.get_settings()
        self.source_language_manager = ServiceLocator.get_source_language_manager()
        self.source_style_scheme_manager = ServiceLocator.get_source_style_scheme_manager()
        self.font_manager = ServiceLocator.get_font_manager()
        self.font_manager.register_observer(self)

        self.mover_mark = self.create_mark('mover', self.get_start_iter(), True)

        # set source language for syntax highlighting
        self.source_language = self.source_language_manager.get_language(self.document.get_gsv_language_name())
        self.set_language(self.source_language)
        self.update_syntax_scheme()

        self.search_settings = GtkSource.SearchSettings()
        self.search_context = GtkSource.SearchContext.new(self, self.search_settings)
        self.search_context.set_highlight(True)

        self.insert_position = 0

        self.synctex_tag_count = 0
        self.synctex_highlight_tags = dict()

        self.indentation_update = None
        self.indentation_tags = dict()
        self.tab_width = self.settings.get_value('preferences', 'tab_width')
        self.settings.register_observer(self)

        self.placeholder_tag = self.create_tag('placeholder')
        self.placeholder_tag.set_property('background', '#fce94f')
        self.placeholder_tag.set_property('foreground', '#000')

        self.connect('mark-set', self.on_mark_set)
        self.connect('mark-deleted', self.on_mark_deleted)
        self.connect('insert-text', self.on_insert_text)
        self.connect('delete-range', self.on_delete_range)

        self.document.add_change_code('buffer_ready')

        self.view.set_left_margin(self.font_manager.get_char_width(self.view) - 3)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'tab_width'):
                self.tab_width = self.settings.get_value('preferences', 'tab_width')

            if (section, item) in [('preferences', 'syntax_scheme'), ('preferences', 'syntax_scheme_dark_mode')]:
                self.update_syntax_scheme()

        if change_code == 'font_string_changed':
            self.view.set_left_margin(self.font_manager.get_char_width(self.view) - 3)

    def update_syntax_scheme(self):
        name = self.settings.get_value('preferences', 'syntax_scheme')
        self.source_style_scheme_light = self.source_style_scheme_manager.get_scheme(name)
        name = self.settings.get_value('preferences', 'syntax_scheme_dark_mode')
        self.source_style_scheme_dark = self.source_style_scheme_manager.get_scheme(name)
        self.set_use_dark_scheme(self.document.dark_mode)

    def on_insert_text(self, buffer, location_iter, text, text_length):
        self.indentation_update = {'line_start': location_iter.get_line(), 'text_length': text_length}
        self.document.add_change_code('text_inserted', (buffer, location_iter, text, text_length))

    def on_delete_range(self, buffer, start_iter, end_iter):
        self.indentation_update = {'line_start': start_iter.get_line(), 'text_length': 0}
        self.document.add_change_code('text_deleted', (buffer, start_iter, end_iter))

    def on_mark_set(self, buffer, insert, mark, user_data=None):
        if mark.get_name() == 'insert':
            self.update_placeholder_selection()
            self.document.add_change_code('insert_mark_set')
        self.update_selection_state()

    def on_mark_deleted(self, buffer, mark, user_data=None):
        if mark.get_name() == 'insert':
            self.document.add_change_code('insert_mark_deleted')
        self.update_selection_state()

    def initially_set_text(self, text):
        self.begin_not_undoable_action()
        self.set_text(text)
        self.end_not_undoable_action()
        self.set_modified(False)

    def get_indentation_tag(self, number_of_characters):
        try:
            tag = self.indentation_tags[number_of_characters]
        except KeyError:
            tag = self.create_tag('indentation-' + str(number_of_characters))
            tag.set_property('indent', -1 * number_of_characters * self.font_manager.get_char_width(self.view))
            self.indentation_tags[number_of_characters] = tag
        return tag

    def update_selection_state(self):
        self.document.add_change_code('selection_might_have_changed')

    #@timer.timer
    def update_indentation_tags(self):
        if self.indentation_update != None:
            start_iter = self.get_iter_at_line(self.indentation_update['line_start'])
            end_iter = start_iter.copy()
            end_iter.forward_chars(self.indentation_update['text_length'])
            end_iter.forward_to_line_end()
            start_iter.set_line_offset(0)
            text = self.get_text(start_iter, end_iter, True)
            for count, line in enumerate(text.splitlines()):
                for tag in start_iter.get_tags():
                    self.remove_tag(tag, start_iter, end_iter)
                number_of_characters = len(line.replace('\t', ' ' * self.tab_width)) - len(line.lstrip())
                if number_of_characters > 0:
                    end_iter = start_iter.copy()
                    end_iter.forward_chars(1)
                    self.apply_tag(self.get_indentation_tag(number_of_characters), start_iter, end_iter)
                start_iter.forward_line()

            self.indentation_update = None

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
        
        package_data = self.document.get_package_details()
        if package_data:
            max_end = 0
            for package in package_data.items():
                if package[1].end() > max_end:
                    max_end = package[1].end()
            insert_iter = self.get_iter_at_offset(max_end)
            if not insert_iter.ends_line():
                insert_iter.forward_to_line_end()
            self.insert_text_at_iter(insert_iter, '\n' + text)
        else:
            end_iter = self.get_end_iter()
            result = end_iter.backward_search('\\documentclass', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
            if result != None:
                result[0].forward_to_line_end()
                self.insert_text_at_iter(result[0], '\n' + text)
            else:
                self.insert_text_at_cursor(text)

    def remove_packages(self, packages):
        packages_dict = self.document.get_package_details()
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

    def replace_range_by_offset_and_length(self, offset, length, text, indent_lines=True, select_dot=True):
        start_iter = self.get_iter_at_offset(offset)
        end_iter = self.get_iter_at_offset(offset + length)
        self.replace_range(start_iter, end_iter, text, indent_lines, select_dot)

    def replace_range(self, start_iter, end_iter, text, indent_lines=True, select_dot=True):
        self.begin_user_action()
        self.replace_range_no_user_action(start_iter, end_iter, text, indent_lines, select_dot)
        self.end_user_action()

    def replace_range_no_user_action(self, start_iter, end_iter, text, indent_lines=True, select_dot=True):
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
            if not line.lstrip().startswith('%'):
                do_comment = True

        if do_comment:
            for line_number in line_numbers:
                self.insert(self.get_iter_at_line(line_number), '%')
        else:
            for line_number in line_numbers:
                line = self.get_line(line_number)
                offset = len(line) - len(line.lstrip())
                start = self.get_iter_at_line(line_number)
                start.forward_chars(offset)
                end = start.copy()
                end.forward_char()
                self.delete(start, end)

        self.end_user_action()

    def add_backslash_with_space(self):
        self.insert_at_cursor('\\ ')
        insert_iter = self.get_iter_at_mark(self.get_insert())
        insert_iter.backward_char()
        self.place_cursor(insert_iter)

    def autoadd_latex_brackets(self, char):
        if self.get_char_before_cursor() == '\\':
            add_char = '\\'
        else:
            add_char = ''
        if char == '[':
            self.begin_user_action()
            self.delete_selection(True, True)
            self.insert_at_cursor('[' + add_char + ']')
            self.end_user_action()
        if char == '{':
            self.begin_user_action()
            self.delete_selection(True, True)
            self.insert_at_cursor('{' + add_char + '}')
            self.end_user_action()
        if char == '(':
            self.begin_user_action()
            self.delete_selection(True, True)
            self.insert_at_cursor('(' + add_char + ')')
            self.end_user_action()
        insert_iter = self.get_iter_at_mark(self.get_insert())
        insert_iter.backward_char()
        if add_char == '\\':
            insert_iter.backward_char()
        self.place_cursor(insert_iter)

    def get_char_at_cursor(self):
        start_iter = self.get_iter_at_mark(self.get_insert())
        end_iter = start_iter.copy()
        end_iter.forward_char()
        return self.get_text(start_iter, end_iter, False)

    def get_char_before_cursor(self):
        start_iter = self.get_iter_at_mark(self.get_insert())
        end_iter = start_iter.copy()
        end_iter.backward_char()
        return self.get_text(start_iter, end_iter, False)

    def get_latex_command_at_cursor(self):
        insert_iter = self.get_iter_at_mark(self.get_insert())
        limit_iter = insert_iter.copy()
        limit_iter.backward_chars(50)
        word_start_iter = insert_iter.copy()
        result = word_start_iter.backward_search('\\', Gtk.TextSearchFlags.TEXT_ONLY, limit_iter)
        if result != None:
            word_start_iter = result[0]
        word = word_start_iter.get_slice(insert_iter)
        return word

    def get_latex_command_at_cursor_offset(self):
        insert_iter = self.get_iter_at_mark(self.get_insert())
        limit_iter = insert_iter.copy()
        limit_iter.backward_chars(50)
        word_start_iter = insert_iter.copy()
        result = word_start_iter.backward_search('\\', Gtk.TextSearchFlags.TEXT_ONLY, limit_iter)
        if result != None:
            word_start_iter = result[0]
            return word_start_iter.get_offset()
        return None

    def replace_latex_command_at_cursor(self, text, dotlabels, is_full_command=False):
        insert_iter = self.get_iter_at_mark(self.get_insert())
        current_word = self.get_latex_command_at_cursor()
        start_iter = insert_iter.copy()
        start_iter.backward_chars(len(current_word))

        if is_full_command and text.startswith('\\begin'):
            end_command = text.replace('\\begin', '\\end')
            end_command_bracket_position = end_command.find('}')
            if end_command_bracket_position:
                end_command = end_command[:end_command_bracket_position + 1]
            text += '\n\t•\n' + end_command
            if self.settings.get_value('preferences', 'spaces_instead_of_tabs'):
                number_of_spaces = self.settings.get_value('preferences', 'tab_width')
                text = text.replace('\t', ' ' * number_of_spaces)
            dotlabels += 'content###'
            if end_command.find('•') >= 0:
                dotlabels += 'environment###'

            line_iter = self.get_iter_at_line(start_iter.get_line())
            ws_line = self.get_text(line_iter, start_iter, False)
            lines = text.split('\n')
            ws_number = len(ws_line) - len(ws_line.lstrip())
            whitespace = ws_line[:ws_number]
            text = ''
            for no, line in enumerate(lines):
                if no != 0:
                    text += '\n' + whitespace
                text += line

        parts = text.split('•')
        if len(parts) == 1:
            orig_text = self.get_text(start_iter, insert_iter, False)
            if parts[0].startswith(orig_text):
                self.insert_at_cursor(parts[0][len(orig_text):])
            else:
                self.replace_range(start_iter, insert_iter, parts[0], indent_lines=True, select_dot=True)
        else:
            self.begin_user_action()

            self.delete(start_iter, insert_iter)
            insert_offset = self.get_iter_at_mark(self.get_insert()).get_offset()
            count = len(parts)
            select_dot_offset = -1
            for part in parts:
                insert_iter = self.get_iter_at_offset(insert_offset)
                insert_offset += len(part.replace('\t', ' ' * self.tab_width))
                self.insert(insert_iter, part)
                if count > 1:
                    insert_iter = self.get_iter_at_offset(insert_offset)
                    self.insert_with_tags(insert_iter, '•', self.placeholder_tag)
                    if select_dot_offset == -1:
                        select_dot_offset = insert_offset
                    insert_offset += 1
                count -= 1
            select_dot_iter = self.get_iter_at_offset(select_dot_offset)
            bound = select_dot_iter.copy()
            bound.forward_chars(1)
            self.select_range(select_dot_iter, bound)

            self.end_user_action()

    def get_line_at_cursor(self):
        return self.get_line(self.get_iter_at_mark(self.get_insert()).get_line())

    def get_line(self, line_number):
        start = self.get_iter_at_line(line_number)
        end = start.copy()
        if not end.ends_line():
            end.forward_to_line_end()
        return self.get_slice(start, end, False)

    def get_all_text(self):
        return self.get_text(self.get_start_iter(), self.get_end_iter(), True)

    def get_text_after_offset(self, offset):
        return self.get_text(self.get_iter_at_offset(offset), self.get_end_iter(), True)

    def get_selected_text(self):
        bounds = self.get_selection_bounds()
        if len(bounds) == 2:
            return self.get_text(bounds[0], bounds[1], True)
        else:
            return None

    def is_empty(self):
        return self.get_end_iter().get_offset() > 0

    def update_placeholder_selection(self):
        if self.get_cursor_offset() != self.insert_position:
            if not self.get_selection_bounds():
                start_iter = self.get_iter_at_mark(self.get_insert())
                prev_iter = start_iter.copy()
                prev_iter.backward_char()
                if start_iter.has_tag(self.placeholder_tag):
                    while start_iter.has_tag(self.placeholder_tag):
                        start_iter.backward_char()
                    if not start_iter.has_tag(self.placeholder_tag):
                        start_iter.forward_char()
                    end_iter = start_iter.copy()

                    tag_length = 0
                    while end_iter.has_tag(self.placeholder_tag):
                        tag_length += 1
                        end_iter.forward_char()

                    moved_backward_from_end = (self.insert_position == self.get_cursor_offset() + tag_length)
                    if not moved_backward_from_end:
                        self.select_range(start_iter, end_iter)
                elif prev_iter.has_tag(self.placeholder_tag):
                    while prev_iter.has_tag(self.placeholder_tag):
                        prev_iter.backward_char()
                    if not prev_iter.has_tag(self.placeholder_tag):
                        prev_iter.forward_char()
                    end_iter = prev_iter.copy()

                    tag_length = 0
                    while end_iter.has_tag(self.placeholder_tag):
                        tag_length += 1
                        end_iter.forward_char()

                    moved_forward_from_start = (self.insert_position == self.get_cursor_offset() - tag_length)
                    if not moved_forward_from_start:
                        self.select_range(prev_iter, end_iter)

            self.insert_position = self.get_cursor_offset()

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
        regex = ServiceLocator.get_regex_object(r'(\W{0,1})' + regex_pattern.replace('\x1b', r'(?:\w{2,3})').replace('\x1c', r'(?:\w{2})').replace('\x1d', r'(?:\w{2,3})').replace('\-', r'(?:-{0,1})') + r'(\W{0,1})')
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

    def get_cursor_offset(self):
        return self.get_iter_at_mark(self.get_insert()).get_offset()

    def get_cursor_line_offset(self):
        return self.get_iter_at_mark(self.get_insert()).get_line_offset()

    def cursor_ends_word(self):
        return self.get_iter_at_mark(self.get_insert()).ends_word()

    def scroll_cursor_onscreen(self):
        self.scroll_mark_onscreen(self.get_insert())

    def scroll_mark_onscreen(self, text_mark):
        self.scroll_iter_onscreen(self.get_iter_at_mark(text_mark))

    def scroll_iter_onscreen(self, text_iter):
        visible_lines = self.get_number_of_visible_lines()
        iter_position = self.view.get_iter_location(text_iter).y
        end_yrange = self.view.get_line_yrange(self.get_end_iter())
        buffer_height = end_yrange.y + end_yrange.height
        line_height = self.font_manager.get_line_height(self.view)
        window_offset = self.view.get_visible_rect().y
        window_height = self.view.get_visible_rect().height
        gap = min(math.floor(max((visible_lines - 2), 0) / 2), 5)
        if iter_position < window_offset + gap * line_height:
            scroll_iter = self.view.get_iter_at_location(0, max(iter_position - gap * line_height, 0)).iter
            self.move_mark(self.mover_mark, scroll_iter)
            self.view.scroll_to_mark(self.mover_mark, 0, False, 0, 0)
            return
        gap = min(math.floor(max((visible_lines - 2), 0) / 2), 8)
        if iter_position > (window_offset + window_height - (gap + 1) * line_height):
            scroll_iter = self.view.get_iter_at_location(0, min(iter_position + gap * line_height, buffer_height)).iter
            self.move_mark(self.mover_mark, scroll_iter)
            self.view.scroll_to_mark(self.mover_mark, 0, False, 0, 0)

    def cut(self):
        self.view.emit('cut-clipboard')

    def copy(self):
        self.view.emit('copy-clipboard')

    def paste(self):
        self.view.emit('paste-clipboard')

    def select_all(self, widget=None):
        self.select_range(self.get_start_iter(), self.get_end_iter())

    def get_number_of_visible_lines(self):
        line_height = self.font_manager.get_line_height(self.view)
        return math.floor(self.view.get_visible_rect().height / line_height)

    def set_use_dark_scheme(self, use_dark_scheme):
        if use_dark_scheme: self.set_style_scheme(self.source_style_scheme_dark)
        else: self.set_style_scheme(self.source_style_scheme_light)


