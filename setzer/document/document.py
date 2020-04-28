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
gi.require_version('GtkSource', '4')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GtkSource
from gi.repository import Gdk
from gi.repository import GObject

import os.path
import time
import re
import difflib

import setzer.document.document_builder as document_builder
import setzer.document.document_controller as document_controller
import setzer.document.document_presenter as document_presenter
import setzer.document.shortcutsbar.shortcutsbar_presenter as shortcutsbar_presenter
import setzer.document.document_viewgtk as document_view
import setzer.document.document_switcher_item.document_switcher_item as document_switcher_item
import setzer.document.build_widget.build_widget as build_widget
import setzer.document.search.search as search
import setzer.document.autocomplete.autocomplete as autocomplete
import setzer.document.spellchecker.spellchecker as spellchecker
import setzer.document.code_folding.code_folding as code_folding
import setzer.document.parser.latex_parser as latex_parser
import setzer.document.parser.bibtex_parser as bibtex_parser
import setzer.document.preview.preview as preview
import setzer.document.state_manager.state_manager_latex as state_manager_latex
import setzer.document.state_manager.state_manager_bibtex as state_manager_bibtex
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator


class Document(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.settings = ServiceLocator.get_settings()

        self.displayname = ''
        self.filename = None
        self.save_date = None
        self.last_activated = 0

        self.source_buffer = None
        self.search_settings = None
        self.search_context = None
        self.parser = None
        self.init_buffer()
        
    def set_search_text(self, search_text):
        self.search_settings.set_search_text(search_text)
        
    def init_buffer(self):
        self.source_buffer = GtkSource.Buffer()

        resources_path = ServiceLocator.get_resources_path()

        # set source language for syntax highlighting
        self.source_language_manager = GtkSource.LanguageManager()
        self.source_language = self.source_language_manager.get_language(self.get_gsv_language_name())
        self.source_buffer.set_language(self.source_language)

        self.source_style_scheme_manager = GtkSource.StyleSchemeManager()
        self.source_style_scheme_manager.set_search_path((os.path.join(resources_path, 'gtksourceview', 'styles'),))
        self.source_style_scheme_light = self.source_style_scheme_manager.get_scheme('setzer')
        self.source_style_scheme_dark = self.source_style_scheme_manager.get_scheme('setzer-dark')

        self.search_settings = GtkSource.SearchSettings()
        self.search_context = GtkSource.SearchContext.new(self.source_buffer, self.search_settings)
        self.search_context.set_highlight(True)

        self.source_buffer.connect('changed', self.on_buffer_changed)
        self.source_buffer.connect('insert-text', self.on_insert_text)

        self.add_change_code('buffer_ready')

    def on_insert_text(self, buffer, location, text, len):
        pass

    def on_buffer_changed(self, buffer):
        try: self.code_folding.on_buffer_changed(buffer)
        except AttributeError: pass

        if self.parser != None:
            self.parser.on_buffer_changed()
        if self.source_buffer.get_end_iter().get_offset() > 0:
            self.add_change_code('document_not_empty')
        else:
            self.add_change_code('document_empty')

    def set_dark_mode(self, dark_mode):
        self.set_use_dark_scheme(dark_mode)
    
    def set_use_dark_scheme(self, use_dark_scheme):
        if use_dark_scheme: self.source_buffer.set_style_scheme(self.source_style_scheme_dark)
        else: self.source_buffer.set_style_scheme(self.source_style_scheme_light)
    
    def get_buffer(self):
        return self.source_buffer

    def set_filename(self, filename):
        self.filename = filename
        self.add_change_code('filename_change', filename)

    def get_filename(self):
        return self.filename
        
    def get_displayname(self):
        if self.filename != None:
            return self.get_filename()
        else:
            return self.displayname
        
    def set_displayname(self, displayname):
        self.displayname = displayname
        self.add_change_code('displayname_change')
        
    def get_last_activated(self):
        return self.last_activated
        
    def set_last_activated(self, date):
        self.last_activated = date
        
    def get_modified(self):
        return self.get_buffer().get_modified()
        
    def populate_from_filename(self):
        if self.filename == None: return False
        if not os.path.isfile(self.filename): return False
        if self.get_buffer() == None: return False

        with open(self.filename) as f:
            text = f.read()
        source_buffer = self.get_buffer()
        source_buffer.begin_not_undoable_action()
        source_buffer.set_text(text)
        source_buffer.end_not_undoable_action()
        source_buffer.set_modified(False)
        source_buffer.place_cursor(source_buffer.get_start_iter())
        self.update_save_date()
        return True
                
    def save_to_disk(self):
        if self.filename == None: return False
        if self.get_buffer() == None: return False
        else:
            text = self.get_text()
            if text != None:
                with open(self.filename, 'w') as f:
                    f.write(text)
                self.update_save_date()
                self.get_buffer().set_modified(False)

    def update_save_date(self):
        self.save_date = os.path.getmtime(self.filename)

    def get_text(self):
        buff = self.get_buffer()
        if buff != None:
            return buff.get_text(buff.get_start_iter(), buff.get_end_iter(), True)
        return None

    def set_initial_folded_regions(self, folded_regions):
        self.code_folding.set_initial_folded_regions(folded_regions)
        
    def place_cursor(self, text_iter):
        buff = self.get_buffer()
        buff.place_cursor(text_iter)
        self.view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)

    def insert_before_document_end(self, text):
        buffer = self.get_buffer()
        end_iter = buffer.get_end_iter()
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
        
        buffer = self.get_buffer()
        end_iter = buffer.get_end_iter()
        result = end_iter.backward_search('\\usepackage', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
        if result != None:
            result[0].forward_to_line_end()
            self.insert_text_at_iter(result[0], '\n' + text)
        else:
            end_iter = buffer.get_end_iter()
            result = end_iter.backward_search('\\documentclass', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
            if result != None:
                result[0].forward_to_line_end()
                self.insert_text_at_iter(result[0], '\n' + text)
            else:
                self.insert_text_at_cursor(text)

    def remove_packages(self, packages):
        packages_dict = self.parser.symbols['packages_detailed']
        for package in packages:
            try:
                match_obj = packages_dict[package]
            except KeyError: return
            start_iter = self.source_buffer.get_iter_at_offset(match_obj.start())
            end_iter = self.source_buffer.get_iter_at_offset(match_obj.end())
            text = self.source_buffer.get_text(start_iter, end_iter, False)
            if text == match_obj.group(0):  
                if start_iter.get_line_offset() == 0:
                    start_iter.backward_char()
                self.source_buffer.delete(start_iter, end_iter)

    def insert_text_at_iter(self, insert_iter, text, indent_lines=True):
        buff = self.get_buffer()
        buff.place_cursor(insert_iter)
        self.insert_text_at_cursor(text, indent_lines)

    def insert_text_at_cursor(self, text, indent_lines=True):
        buff = self.get_buffer()
        if buff != False:
            buff.begin_user_action()

            # replace tabs with spaces, if set in preferences
            if self.settings.get_value('preferences', 'spaces_instead_of_tabs'):
                number_of_spaces = self.settings.get_value('preferences', 'tab_width')
                text = text.replace('\t', ' ' * number_of_spaces)

            dotcount = text.count('•')
            insert_iter = buff.get_iter_at_mark(buff.get_insert())
            bounds = buff.get_selection_bounds()
            selection = ''
            if dotcount == 1:
                bounds = buff.get_selection_bounds()
                if len(bounds) > 0:
                    selection = buff.get_text(bounds[0], bounds[1], True)
                    if len(selection) > 0:
                        text = text.replace('•', selection, 1)

            if indent_lines:
                line_iter = buff.get_iter_at_line(insert_iter.get_line())
                ws_line = buff.get_text(line_iter, insert_iter, False)
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

            buff.delete_selection(False, False)
            buff.insert_at_cursor(final_text)

            dotindex = final_text.find('•')
            if dotcount > 0:
                selection_len = len(selection) if dotcount == 1 else 0
                start = buff.get_iter_at_mark(buff.get_insert())
                start.backward_chars(abs(dotindex + selection_len - len(final_text)))
                buff.place_cursor(start)
                end = start.copy()
                end.forward_char()
                buff.select_range(start, end)
            self.view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)

            buff.end_user_action()

    def replace_range(self, start_iter, end_iter, text, indent_lines=True):
        buffer = self.get_buffer()
        if buffer != None:
            buffer.begin_user_action()

            if indent_lines:
                line_iter = buffer.get_iter_at_line(start_iter.get_line())
                ws_line = buffer.get_text(line_iter, start_iter, False)
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

            buffer.delete(start_iter, end_iter)
            buffer.insert(start_iter, final_text)

            dotindex = final_text.find('•')
            if dotindex > -1:
                start_iter.backward_chars(abs(dotindex - len(final_text)))
                bound = start_iter.copy()
                bound.forward_chars(1)
                buffer.select_range(start_iter, bound)
            buffer.end_user_action()

    def insert_before_after(self, before, after):
        ''' wrap text around current selection. '''

        buff = self.get_buffer()
        if buff != False:
            bounds = buff.get_selection_bounds()

            if len(bounds) > 1:
                text = before + buff.get_text(*bounds, 0) + after
                self.replace_range(bounds[0], bounds[1], text)
            else:
                text = before + '•' + after
                self.insert_text_at_cursor(text)


class LaTeXDocument(Document):

    def __init__(self):
        Document.__init__(self)
        self.is_master = False
        self.has_visible_build_system = False

        # possible states: idle, ready_for_building
        # building_in_progress, building_to_stop
        self.build_state = 'idle'

        # possible values: build, forward_sync, build_and_forward_sync
        self.build_mode = 'build_and_forward_sync'
        self.build_pathname = None
        self.can_forward_sync = False
        self.can_backward_sync = False
        self.backward_sync_data = None
        self.synctex_tag_count = 0
        self.synctex_highlight_tags = dict()

        self.preview = preview.Preview(self)
        self.state_manager = state_manager_latex.StateManagerLaTeX(self)
        self.view = document_view.DocumentView(self)
        self.document_switcher_item = document_switcher_item.DocumentSwitcherItemLaTeX(self)
        self.search = search.Search(self, self.view, self.view.search_bar)

        self.build_log_items = list()
        self.has_been_built = False
        self.last_build_start_time = None
        self.build_time = None
        self.build_widget = build_widget.BuildWidget(self)

        self.autocomplete = autocomplete.Autocomplete(self, self.view)
        self.builder = document_builder.DocumentBuilder(self)
        self.presenter = document_presenter.DocumentPresenter(self, self.view)
        self.shortcutsbar = shortcutsbar_presenter.ShortcutsbarPresenter(self, self.view)
        self.code_folding = code_folding.CodeFolding(self)
        self.controller = document_controller.DocumentController(self, self.view)

        self.spellchecker = spellchecker.Spellchecker(self.view.source_view)
        self.parser = latex_parser.LaTeXParser(self)

        self.update_can_forward_sync()
        self.update_can_backward_sync()

    def change_build_state(self, state):
        self.build_state = state

        if self.build_mode in ['build', 'build_and_forward_sync']:
            if state == 'ready_for_building':
                self.build_time = None
            elif state == 'building_in_progress':
                self.last_build_start_time = time.time()
            elif state == 'building_to_stop':
                pass
            elif state == 'idle':
                pass
            self.add_change_code('build_state_change', self.build_state)
        else:
            self.add_change_code('build_state_change', self.build_state)

    def show_build_state(self, message):
        self.add_change_code('build_state', message)

    def get_build_state(self):
        return self.build_state

    def set_build_mode(self, mode):
        self.build_mode = mode

    def get_build_mode(self):
        return self.build_mode

    def set_build_pathname(self, pathname):
        self.build_pathname = pathname
        self.update_can_forward_sync()
        self.update_can_backward_sync()

    def update_can_forward_sync(self):
        if self.build_pathname != None and self.preview.pdf_loaded:
            self.can_forward_sync = True
        else:
            self.can_forward_sync = False
        self.add_change_code('can_forward_sync_changed', self.can_forward_sync)

    def update_can_backward_sync(self):
        if self.build_pathname != None and self.preview.pdf_loaded:
            self.can_backward_sync = True
        else:
            self.can_backward_sync = False
        self.add_change_code('can_backward_sync_changed', self.can_backward_sync)

    def forward_sync(self):
        if self.can_forward_sync:
            self.set_build_mode('forward_sync')
            self.start_building()

    def backward_sync(self, page, x, y, word, context):
        if self.can_backward_sync:
            self.backward_sync_data = {'page': page, 'x': x, 'y': y, 'word': word, 'context': context}
            self.set_build_mode('backward_sync')
            self.start_building()

    def build_and_forward_sync(self):
        self.set_build_mode('build_and_forward_sync')
        self.start_building()

    def start_building(self):
        if self.build_mode == 'forward_sync' and self.build_pathname == None: return
        if self.build_mode == 'backward_sync' and self.backward_sync_data == None: return
        if self.filename == None: return

        self.change_build_state('ready_for_building')

    def stop_building(self):
        self.change_build_state('building_to_stop')
        
    def cleanup_build_files(self):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,'.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
        for ending in file_endings:
            filename = os.path.splitext(self.get_filename())[0] + ending
            try: os.remove(filename)
            except FileNotFoundError: pass
        self.add_change_code('cleaned_up_build_files')

    def set_is_master(self, is_master):
        self.is_master = is_master
        self.add_change_code('master_state_change', is_master)

    def set_has_visible_build_system(self, has_visible_build_system):
        if self.has_visible_build_system != has_visible_build_system:
            self.has_visible_build_system = has_visible_build_system
            self.add_change_code('build_system_visibility_change', has_visible_build_system)

    def set_synctex_position(self, position):
        buff = self.get_buffer()
        if buff != None:
            start = buff.get_iter_at_line(position['line'])
            end = start.copy()
            if not start.ends_line():
                end.forward_to_line_end()
            text = buff.get_text(start, end, False)

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
        buff = self.get_buffer()
        buff.place_cursor(start_iter)
        self.synctex_tag_count += 1
        self.source_buffer.create_tag('synctex_highlight-' + str(self.synctex_tag_count), background_rgba=Gdk.RGBA(0.976, 0.941, 0.420, 0.6), background_full_height=True)
        tag = self.source_buffer.get_tag_table().lookup('synctex_highlight-' + str(self.synctex_tag_count))
        self.source_buffer.apply_tag(tag, start_iter, end_iter)
        if not self.synctex_highlight_tags:
            GObject.timeout_add(15, self.remove_or_color_synctex_tags)
        self.synctex_highlight_tags[self.synctex_tag_count] = {'tag': tag, 'time': time.time()}
        self.view.source_view.scroll_mark_onscreen(buff.get_insert())

    def get_synctex_word_bounds(self, text, word, context):
        if not word: return None
        word = word.split(' ')
        if len(word) > 2:
            word = word[:2]
        word = ' '.join(word)
        regex = re.escape(word)

        for c in regex:
            if ord(c) > 127:
                regex = regex.replace(c, '(?:\w)')

        matches = list()
        top_score = 0.1
        for match in re.finditer('(\W{0,1})' + regex.replace('\x1b', '(?:\w{2,3})').replace('\x1c', '(?:\w{2})').replace('\x1d', '(?:\w{2,3})').replace('\-', '(?:-{0,1})') + '(\W{0,1})', text):
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
        buff = self.get_buffer()
        if buff != None:
            for tag_count in list(self.synctex_highlight_tags):
                item = self.synctex_highlight_tags[tag_count]
                time_factor = time.time() - item['time']
                if time_factor > 1.5:
                    if time_factor <= 1.75:
                        opacity_factor = 1 - (time_factor - 1.5) * 4
                        item['tag'].set_property('background-rgba', Gdk.RGBA(0.976, 0.941, 0.420, opacity_factor * 0.6))
                    else:
                        start = self.source_buffer.get_start_iter()
                        end = self.source_buffer.get_end_iter()
                        self.source_buffer.remove_tag(item['tag'], start, end)
                        self.source_buffer.get_tag_table().remove(item['tag'])
                        del(self.synctex_highlight_tags[tag_count])
        return bool(self.synctex_highlight_tags)

    def get_folded_regions(self):
        return self.code_folding.get_folded_regions()

    def get_file_ending(self):
        return 'tex'

    def is_latex_document(self):
        return True

    def is_bibtex_document(self):
        return False

    def get_gsv_language_name(self):
        return 'latex'


class BibTeXDocument(Document):

    def __init__(self):
        Document.__init__(self)
        self.is_master = False

        self.state_manager = state_manager_bibtex.StateManagerBibTeX(self)
        self.view = document_view.DocumentView(self)
        self.document_switcher_item = document_switcher_item.DocumentSwitcherItemBibTeX(self)
        self.search = search.Search(self, self.view, self.view.search_bar)

        self.autocomplete = None
        self.builder = None
        self.presenter = document_presenter.DocumentPresenter(self, self.view)
        self.shortcutsbar = shortcutsbar_presenter.ShortcutsbarPresenter(self, self.view)
        self.controller = document_controller.DocumentController(self, self.view)

        self.parser = bibtex_parser.BibTeXParser()

    def get_folded_regions(self):
        return []

    def get_file_ending(self):
        return 'bib'

    def is_latex_document(self):
        return False

    def is_bibtex_document(self):
        return True

    def get_gsv_language_name(self):
        return 'bibtex'


