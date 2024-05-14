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
gi.require_version('GtkSource', '5')
gi.require_version('Gtk', '4.0')
from gi.repository import GtkSource, Gtk, GObject

import os.path, time

import setzer.document.document_controller as document_controller
import setzer.document.document_presenter as document_presenter
import setzer.document.document_viewgtk as document_view
import setzer.document.search.search as search
import setzer.document.gutter.gutter as gutter
import setzer.document.parser.parser_latex as parser_latex
import setzer.document.parser.parser_bibtex as parser_bibtex
import setzer.document.parser.parser_dummy as parser_dummy
import setzer.document.code_folding.code_folding as code_folding
import setzer.document.bracket_completion.bracket_completion as bracket_completion
import setzer.document.update_matching_blocks.update_matching_blocks as update_matching_blocks
import setzer.document.autocomplete.autocomplete as autocomplete
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator
from setzer.app.color_manager import ColorManager
from setzer.app.font_manager import FontManager


class Document(Observable):

    def __init__(self, language):
        Observable.__init__(self)
        self.language = language

        self.displayname = ''
        self.filename = None
        self.save_date = None
        self.last_activated = 0
        self.is_root = False
        self.root_is_set = False
        self.highlight_tag_count = 0
        self.highlight_tags = dict()

        self.source_buffer = GtkSource.Buffer()
        self.source_buffer.set_language(ServiceLocator.get_source_language(language))
        self.source_view = GtkSource.View.new_with_buffer(self.source_buffer)
        self.source_buffer.set_style_scheme(ServiceLocator.get_style_scheme())
        self.source_buffer.connect('modified-changed', self.on_modified_change)
        self.source_buffer.connect('changed', self.on_change)
        self.source_buffer.connect('notify::cursor-position', self.on_cursor_position_change)
        self.settings = ServiceLocator.get_settings()

        self.view = document_view.DocumentView(self)
        self.presenter = document_presenter.DocumentPresenter(self, self.view)
        self.controller = document_controller.DocumentController(self, self.view)

        if self.is_latex_document(): self.parser = parser_latex.ParserLaTeX(self)
        elif self.is_bibtex_document(): self.parser = parser_bibtex.ParserBibTeX(self)
        else: self.parser = parser_dummy.ParserDummy(self)
        self.code_folding = code_folding.CodeFolding(self)
        self.gutter = gutter.Gutter(self, self.view)
        self.search = search.Search(self, self.view)
        if self.is_latex_document(): self.update_matching_blocks = update_matching_blocks.UpdateMatchingBlocks(self)
        if self.is_latex_document(): self.bracket_completion = bracket_completion.BracketCompletion(self)
        if self.is_latex_document(): self.autocomplete = autocomplete.Autocomplete(self)

        self.settings.connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'color_scheme':
            self.source_buffer.set_style_scheme(ServiceLocator.get_style_scheme())

    def set_filename(self, filename):
        if filename == None:
            self.filename = filename
        else:
            self.filename = os.path.realpath(filename)
        self.add_change_code('filename_change', filename)

    def get_filename(self):
        return self.filename
        
    def get_dirname(self):
        if self.filename != None:
            return os.path.dirname(self.filename)
        else:
            return ''

    def get_displayname(self):
        if self.filename != None:
            return self.get_filename()
        else:
            return self.displayname
        
    def set_displayname(self, displayname):
        self.displayname = displayname
        self.add_change_code('displayname_change')

    def get_basename(self):
        if self.filename != None:
            return os.path.basename(self.filename)
        else:
            return self.displayname

    def get_last_activated(self):
        return self.last_activated
        
    def set_last_activated(self, date):
        self.last_activated = date

    def populate_from_filename(self):
        if self.filename == None: return False
        if not os.path.isfile(self.filename):
            self.set_filename(None)
            return False

        with open(self.filename) as f:
            text = f.read()

        self.source_buffer.begin_irreversible_action()
        self.source_buffer.set_text(text)
        self.source_buffer.end_irreversible_action()
        self.source_buffer.set_modified(False)
        self.place_cursor(0, 0)
        self.update_save_date()
        return True

    def save_to_disk(self):
        if self.filename == None: return False

        text = self.get_all_text()
        if text == None: return False

        dirname = os.path.dirname(self.filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(self.filename, 'w') as f:
            f.write(text)
        self.update_save_date()
        self.controller.deleted_on_disk_dialog_shown_after_last_save = False
        self.source_buffer.set_modified(False)

    def update_save_date(self):
        self.save_date = os.path.getmtime(self.filename)

    def get_changed_on_disk(self):
        return self.save_date <= os.path.getmtime(self.filename) - 0.001

    def get_deleted_on_disk(self):
        return not os.path.isfile(self.filename)

    def set_root_state(self, is_root, root_is_set):
        self.is_root = is_root
        self.root_is_set = root_is_set
        self.add_change_code('is_root_changed', is_root)

    def get_is_root(self):
        return self.is_root

    def is_latex_document(self):
        return self.language == 'latex'

    def is_bibtex_document(self):
        return self.language == 'bibtex'

    def get_document_type(self):
        return self.language

    def get_all_text(self):
        return self.source_buffer.get_text(self.source_buffer.get_start_iter(), self.source_buffer.get_end_iter(), True)

    def get_selected_text(self):
        bounds = self.source_buffer.get_selection_bounds()
        if len(bounds) == 2:
            return self.source_buffer.get_text(bounds[0], bounds[1], True)
        else:
            return None

    def get_line(self, line_number):
        found, start_iter = self.source_buffer.get_iter_at_line(line_number)
        end_iter = start_iter.copy()
        if not end_iter.ends_line():
            end_iter.forward_to_line_end()
        return self.source_buffer.get_slice(start_iter, end_iter, False)

    def get_line_after_offset(self, offset):
        start_iter = self.source_buffer.get_iter_at_offset(offset)
        return self.get_line(start_iter.get_line())[start_iter.get_line_offset():]

    def get_chars_at_cursor(self, number_of_chars):
        return self.get_chars_at_iter(self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert()), number_of_chars)

    def get_chars_at_iter(self, start_iter, number_of_chars):
        end_iter = start_iter.copy()
        end_iter.forward_chars(number_of_chars)
        return self.source_buffer.get_text(start_iter, end_iter, False)

    def place_cursor(self, line_number, offset=0):
        _, text_iter = self.source_buffer.get_iter_at_line_offset(line_number, offset)
        self.source_buffer.place_cursor(text_iter)

    def delete_selection(self):
        self.source_buffer.delete_selection(True, True)

    def select_all(self, widget=None):
        self.source_buffer.select_range(self.source_buffer.get_start_iter(), self.source_buffer.get_end_iter())

    def add_packages(self, packages):
        first_package = True
        text = ''
        for packagename in packages:
            if not first_package: text += '\n'
            text += '\\usepackage{' + packagename + '}'
            first_package = False
        self.insert_text_after_packages_if_possible(text)

    def insert_text_after_packages_if_possible(self, text):
        self.source_buffer.begin_user_action()
        package_data = self.parser.symbols['packages_detailed']
        if package_data:
            max_end = 0
            for package_match_list in package_data.values():
                for package_match in package_match_list:
                    offset, match_obj = package_match
                    if offset > max_end:
                        max_end = offset + match_obj.end() - match_obj.start()
            insert_iter = self.source_buffer.get_iter_at_offset(max_end)
            if not insert_iter.ends_line():
                insert_iter.forward_to_line_end()
            self.source_buffer.place_cursor(insert_iter)
            text = '\n' + text
        else:
            end_iter = self.source_buffer.get_end_iter()
            result = end_iter.backward_search('\\documentclass', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
            if result != None:
                result[0].forward_to_line_end()
                self.source_buffer.place_cursor(result[0])
                text = '\n' + text

        self.source_buffer.delete_selection(False, False)
        self.source_buffer.insert_at_cursor(text)
        self.source_buffer.end_user_action()

    def remove_packages(self, packages):
        packages_data = self.parser.symbols['packages_detailed']
        for package in packages:
            if package in packages_data:
                self.source_buffer.begin_user_action()

                for package_match in reversed(packages_data[package]):
                    offset, match_obj = package_match
                    start_iter = self.source_buffer.get_iter_at_offset(offset)
                    end_iter = self.source_buffer.get_iter_at_offset(offset + match_obj.end() - match_obj.start())
                    text = self.source_buffer.get_text(start_iter, end_iter, False)
                    if text == match_obj.group(0):  
                        if start_iter.get_line_offset() == 0:
                            start_iter.backward_char()
                        self.source_buffer.delete(start_iter, end_iter)

                self.source_buffer.end_user_action()

    def insert_before_document_end(self, text):
        end_iter = self.source_buffer.get_end_iter()
        result = end_iter.backward_search('\\end{document}', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
        if result != None:
            self.source_buffer.begin_user_action()
            self.source_buffer.place_cursor(result[0])
            self.source_buffer.insert_at_cursor('''
''' + text + '''

''')
            self.source_buffer.end_user_action()
        else:
            self.source_buffer.insert_at_cursor(text)

    def replace_tabs_with_spaces_if_set(self, text):
        if self.settings.get_value('preferences', 'spaces_instead_of_tabs'):
            number_of_spaces = self.settings.get_value('preferences', 'tab_width')
            text = text.replace('\t', ' ' * number_of_spaces)
        return text

    def indent_text_with_whitespace_at_iter(self, text, start_iter):
        found, line_iter = self.source_buffer.get_iter_at_line(start_iter.get_line())
        ws_line = self.source_buffer.get_text(line_iter, start_iter, False)
        lines = text.split('\n')
        ws_number = len(ws_line) - len(ws_line.lstrip())
        whitespace = ws_line[:ws_number]
        final_text = ''
        for no, line in enumerate(lines):
            if no != 0:
                final_text += '\n' + whitespace
            final_text += line
        return final_text

    def on_modified_change(self, buffer):
        self.add_change_code('modified_changed')

    def on_change(self, buffer):
        self.add_change_code('changed')
        self.scroll_cursor_onscreen(margin_lines=0)

    def on_cursor_position_change(self, buffer, location):
        self.add_change_code('cursor_position_changed')
        self.scroll_cursor_onscreen(margin_lines=0)
        return True

    def select_first_dot_around_cursor(self, offset_before, offset_after):
        end_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        start_iter = end_iter.copy()
        start_iter.backward_chars(offset_before)
        end_iter.forward_chars(offset_after)
        result = start_iter.forward_search('•', 0, end_iter)
        if result != None:
            self.source_buffer.select_range(result[0], result[1])

    def select_next_placeholder(self):
        if self.dot_selected():
            insert = self.source_buffer.get_selection_bounds()[1]
        else:
            insert = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())

        limit_iter = insert.copy()
        limit_iter.forward_lines(5)
        limit_iter.backward_chars(1)
        result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
        if result != None:
            self.source_buffer.select_range(result[0], result[1])
            self.scroll_cursor_onscreen()

    def select_previous_placeholder(self):
        if self.dot_selected():
            insert = self.source_buffer.get_selection_bounds()[0]
        else:
            insert = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())

        limit_iter = insert.copy()
        limit_iter.backward_lines(5)
        result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
        if result != None:
            self.source_buffer.select_range(result[0], result[1])
            self.scroll_cursor_onscreen()

    def dot_selected(self):
        return self.get_selected_text() == '•'

    def highlight_section(self, start_iter, end_iter):
        self.highlight_tag_count += 1
        color = ColorManager.get_ui_color('highlight_tag_textview')
        self.source_buffer.create_tag('highlight-' + str(self.highlight_tag_count), background_rgba=color, background_full_height=True)
        tag = self.source_buffer.get_tag_table().lookup('highlight-' + str(self.highlight_tag_count))
        self.source_buffer.apply_tag(tag, start_iter, end_iter)
        if not self.highlight_tags:
            GObject.timeout_add(15, self.remove_or_color_highlight_tags)
        self.highlight_tags[self.highlight_tag_count] = {'tag': tag, 'time': time.time()}

    def remove_or_color_highlight_tags(self):
        for tag_count in list(self.highlight_tags):
            item = self.highlight_tags[tag_count]
            time_factor = time.time() - item['time']
            if time_factor > 1.5:
                if time_factor <= 1.75:
                    opacity_factor = int(self.ease(1 - (time_factor - 1.5) * 4) * 20)
                    color = ColorManager.get_ui_color('highlight_tag_textview')
                    color.alpha *= opacity_factor * 0.05
                    item['tag'].set_property('background-rgba', color)
                else:
                    start = self.source_buffer.get_start_iter()
                    end = self.source_buffer.get_end_iter()
                    self.source_buffer.remove_tag(item['tag'], start, end)
                    self.source_buffer.get_tag_table().remove(item['tag'])
                    del(self.highlight_tags[tag_count])
        return bool(self.highlight_tags)

    def ease(self, factor): return (factor - 1)**3 + 1

    def scroll_cursor_onscreen(self, margin_lines=5):
        height = self.view.scrolled_window.get_allocated_height()
        if height > 0:
            margin = margin_lines / (height / FontManager.get_line_height(self.source_view))

            self.view.scrolled_window.set_kinetic_scrolling(False)
            self.source_view.scroll_to_mark(self.source_buffer.get_insert(), margin, False, 0, 0)
            self.view.scrolled_window.set_kinetic_scrolling(True)


