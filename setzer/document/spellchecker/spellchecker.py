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
gi.require_version('Spelling', '1')
from gi.repository import Gtk, Spelling

from setzer.app.service_locator import ServiceLocator


provider = None
checker = None


def get_provider():
    ''' The spellchecking backend, enchant in practice. '''

    global provider

    if provider == None:
        try:
            Spelling.init()
            provider = Spelling.Provider.get_default()
        except Exception as error:
            # the typelib can be installed without the library itself
            raise ValueError('libspelling is not usable: ' + str(error))
    return provider


def get_languages():
    ''' All installed dictionaries as a list of (code, name), sorted by name. '''

    languages = [(info.get_code(), info.get_name()) for info in get_provider().list_languages()]
    return sorted(languages, key=lambda item: item[1])


def get_language_code():
    ''' The language to check with: the one from settings if its dictionary is
        installed, the systems default otherwise. '''

    language_code = ServiceLocator.get_settings().get_value('preferences', 'spellchecking_language_code')

    if language_code == None or not get_provider().supports_language(language_code):
        language_code = get_provider().get_default_code()
    return language_code


def get_checker():
    ''' One checker for all documents, so that added and ignored words are
        shared between them. '''

    global checker

    if checker == None:
        checker = Spelling.Checker.new(get_provider(), get_language_code())
    return checker


def is_available():
    return get_provider() != None and get_language_code() != None


class Spellchecker(object):
    ''' Inline spellchecking for a single document, backed by libspelling.

        Regions marked with the "no-spell-check" context class in the language
        spec (latex commands, math, urls, ...) are skipped by libspelling
        itself, no filtering is done here. '''

    def __init__(self, document):
        if not is_available(): raise ValueError('no spellchecking dictionaries installed')

        self.document = document
        self.settings = ServiceLocator.get_settings()

        self.word = None
        self.word_start_offset = None
        self.word_end_offset = None

        self.adapter = Spelling.TextBufferAdapter.new(document.source_buffer, get_checker())
        self.adapter.set_language(get_language_code())
        self.adapter.set_enabled(self.settings.get_value('preferences', 'inline_spellchecking'))

        self.settings.connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'inline_spellchecking':
            self.set_enabled(value)
        elif item == 'spellchecking_language_code':
            self.set_language(value)

    def set_enabled(self, value):
        self.adapter.set_enabled(value)

    def get_enabled(self):
        return self.adapter.get_enabled()

    def set_language(self, language_code):
        if language_code == None or not get_provider().supports_language(language_code):
            language_code = get_provider().get_default_code()
        if language_code == None: return

        self.adapter.set_language(language_code)
        self.adapter.invalidate_all()

    def set_word_at_location(self, x, y):
        ''' Look for a misspelled word at the given position in the source view
            and remember it for the spellchecking actions. Returns the word or
            None if there is none. '''

        self.word = None
        self.word_start_offset = None
        self.word_end_offset = None

        if not self.get_enabled(): return None

        tag = self.adapter.get_tag()
        if tag == None: return None

        source_view = self.document.view.source_view
        buffer_x, buffer_y = source_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, x, y)
        has_iter, start_iter = source_view.get_iter_at_location(buffer_x, buffer_y)
        if not has_iter: return None

        end_iter = start_iter.copy()
        if start_iter.has_tag(tag):
            if not start_iter.starts_tag(tag): start_iter.backward_to_tag_toggle(tag)
            end_iter.forward_to_tag_toggle(tag)
        elif start_iter.ends_tag(tag):
            start_iter.backward_to_tag_toggle(tag)
        else:
            return None

        word = self.document.source_buffer.get_text(start_iter, end_iter, False)
        if word == '': return None

        self.word = word
        self.word_start_offset = start_iter.get_offset()
        self.word_end_offset = end_iter.get_offset()
        return word

    def get_corrections(self):
        if self.word == None: return []

        return get_checker().list_corrections(self.word) or []

    def replace_word(self, replacement):
        if self.word == None: return

        buffer = self.document.source_buffer
        buffer.begin_user_action()
        start_iter = buffer.get_iter_at_offset(self.word_start_offset)
        end_iter = buffer.get_iter_at_offset(self.word_end_offset)
        buffer.delete(start_iter, end_iter)
        buffer.insert(start_iter, replacement)
        buffer.end_user_action()
        self.word = None

    def add_word_to_dictionary(self):
        if self.word == None: return

        get_checker().add_word(self.word)
        self.word = None
        self.invalidate_all_documents()

    def ignore_word(self):
        if self.word == None: return

        get_checker().ignore_word(self.word)
        self.word = None
        self.invalidate_all_documents()

    def invalidate_all_documents(self):
        ''' Added and ignored words are shared, so every open document has to
            be checked again. '''

        for document in ServiceLocator.get_workspace().get_all_documents():
            if document.spellchecker != None:
                document.spellchecker.adapter.invalidate_all()
