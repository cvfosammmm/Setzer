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
from gi.repository import Gtk
from gi.repository import GLib

from setzer.dialogs.document_wizard.pages.page import Page, PageView
from setzer.app.service_locator import ServiceLocator

import os
import re


class GeneralSettingsPage(Page):

    def __init__(self, current_values):
        self.current_values = current_values
        self.view = GeneralSettingsPageView()

    def observe_view(self):
        def text_deleted(buffer, position, n_chars, field_name):
            self.current_values[field_name] = buffer.get_text()

        def text_inserted(buffer, position, chars, n_chars, field_name):
            self.current_values[field_name] = buffer.get_text()

        def language_toggled(button):
            if button.get_active():
                for btn in self.view.language_buttons:
                    if btn is not button:
                        btn.set_active(False)
                    else:
                        self.update_languages_list(re.search(r'\((.*?)\)', btn.get_label()).group(1))

        def language_changed(combobox):
            code = combobox.get_active_id()
            if code != 0:
                self.update_languages_list(code)

        def option_toggled(button, package_name):
            self.current_values['packages'][package_name] = button.get_active()

        def package_hover_start(button, x, y, package_name):
            markup = self.view.packages_tooltip_data[package_name]
            self.view.packages_tooltip.set_markup(markup)

        def package_hover_end(button, package_name):
            self.view.packages_tooltip.set_markup(' ')

        self.view.title_entry.get_buffer().connect('deleted-text', text_deleted, 'title')
        self.view.title_entry.get_buffer().connect('inserted-text', text_inserted, 'title')
        self.view.author_entry.get_buffer().connect('deleted-text', text_deleted, 'author')
        self.view.author_entry.get_buffer().connect('inserted-text', text_inserted, 'author')
        self.view.date_entry.get_buffer().connect('deleted-text', text_deleted, 'date')
        self.view.date_entry.get_buffer().connect('inserted-text', text_inserted, 'date')

        for btn in self.view.language_buttons:
            btn.connect('toggled', language_toggled)
        self.view.language_combobox.connect('changed', language_changed)

        for name, checkbox in self.view.option_packages.items():
            checkbox.connect('toggled', option_toggled, name)
            motion_controller = Gtk.EventControllerMotion()
            motion_controller.connect('enter', package_hover_start, name)
            motion_controller.connect('leave', package_hover_end, name)
            checkbox.add_controller(motion_controller)

    def load_presets(self, presets):
        try:
            text = presets['author']
        except TypeError:
            text = self.current_values['author']
        self.view.author_entry.set_text(text)
        self.view.title_entry.set_text('')
        self.view.date_entry.set_text('\\today')

        try:
            langs = presets['languages']
        except (TypeError, KeyError):
            langs = self.current_values['languages']
        self.current_values['languages'] = langs
        self.add_languages_list(langs)

        for name, option in self.view.option_packages.items():
            try:
                is_active = presets['packages'][name]
            except (TypeError, KeyError):
                is_active = self.current_values['packages'][name]
            option.set_active(is_active)

    def on_activation(self):
        self.view.title_entry.grab_focus()

    def add_languages_list(self, langs):
        self.view.language_combobox.remove_all()
        for index, (code, language) in enumerate(langs.items()):
            label = '{} ({})'.format(language, code)
            if index < len(self.view.language_buttons):
                self.view.language_buttons[index].set_label(label)
            else:
                self.view.language_combobox.append(code, label)
        self.view.language_combobox.prepend_text(_('Others…'))
        self.view.language_combobox.set_active(0)
        self.view.language_buttons[0].set_active(True)

    def update_languages_list(self, lang):
        dictionary = self.current_values['languages']

        if lang in dictionary:
            value = dictionary.pop(lang)
            dictionary = {lang: value, **dictionary}

            self.current_values['languages'] = dictionary
            self.add_languages_list(dictionary)


class GeneralSettingsPageView(PageView):

    def __init__(self):
        PageView.__init__(self)

        self.header.set_text(_('General document settings'))
        self.headerbar_subtitle = _('Step') + ' 3: ' + _('General document settings')

        self.subheader_title = Gtk.Label.new(_('Title'))
        self.subheader_title.get_style_context().add_class('document-wizard-subheader')
        self.subheader_title.set_xalign(0)
        self.title_entry = Gtk.Entry()
        self.title_entry.set_margin_end(280)
        self.subheader_author = Gtk.Label.new(_('Author'))
        self.subheader_author.get_style_context().add_class('document-wizard-subheader')
        self.subheader_author.set_xalign(0)
        self.author_entry = Gtk.Entry()
        self.author_entry.set_margin_end(100)
        self.author_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.author_box.append(self.subheader_author)
        self.author_box.append(self.author_entry)
        self.author_box.set_size_request(348, -1)
        self.subheader_date = Gtk.Label.new(_('Date'))
        self.subheader_date.get_style_context().add_class('document-wizard-subheader')
        self.subheader_date.set_xalign(0)
        self.date_entry = Gtk.Entry()
        self.date_entry.set_margin_end(100)
        self.date_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.date_box.append(self.subheader_date)
        self.date_box.append(self.date_entry)
        self.date_box.set_size_request(348, -1)
        self.subheader_language = Gtk.Label.new(_('Language'))
        self.subheader_language.get_style_context().add_class('document-wizard-subheader')
        self.subheader_language.set_xalign(0)
        self.subheader_language.set_margin_top(18)

        self.language_buttons = []
        self.language_buttons.append(Gtk.ToggleButton.new())
        self.language_buttons.append(Gtk.ToggleButton.new())
        self.language_combobox = Gtk.ComboBoxText()

        self.language_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.language_box.get_style_context().add_class('linked')
        self.language_box.append(self.language_buttons[0])
        self.language_box.append(self.language_buttons[1])
        self.language_box.append(self.language_combobox)

        self.language_description = Gtk.Label.new(_('The main language for this document. This is used to apply rules for hyphenation and other purposes.'))
        self.language_description.set_xalign(0)
        self.language_description.set_margin_top(6)
        self.language_description.get_style_context().add_class('document-wizard-desc')
        self.document_properties_hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.document_properties_hbox.set_margin_top(18)
        self.document_properties_hbox.append(self.author_box)
        self.document_properties_hbox.append(self.date_box)

        self.subheader_packages = Gtk.Label.new(_('Packages'))
        self.subheader_packages.get_style_context().add_class('document-wizard-subheader')
        self.subheader_packages.set_margin_top(18)
        self.subheader_packages.set_xalign(0)
        
        self.option_packages = dict()
        self.option_packages['ams'] = Gtk.CheckButton.new_with_label(_('AMS math packages'))
        self.option_packages['textcomp'] = Gtk.CheckButton.new_with_label('textcomp')
        self.option_packages['graphicx'] = Gtk.CheckButton.new_with_label('graphicx')
        self.option_packages['color'] = Gtk.CheckButton.new_with_label('color')
        self.option_packages['xcolor'] = Gtk.CheckButton.new_with_label('xcolor')
        self.option_packages['url'] = Gtk.CheckButton.new_with_label('url')
        self.option_packages['hyperref'] = Gtk.CheckButton.new_with_label('hyperref')
        self.option_packages['theorem'] = Gtk.CheckButton.new_with_label('theorem')
        self.option_packages['listings'] = Gtk.CheckButton.new_with_label('listings')
        self.option_packages['glossaries'] = Gtk.CheckButton.new_with_label('glossaries')
        self.option_packages['parskip'] = Gtk.CheckButton.new_with_label('parskip')

        self.packages_leftbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.packages_leftbox.set_size_request(348, -1)
        self.packages_leftbox.append(self.option_packages['ams'])
        self.packages_leftbox.append(self.option_packages['textcomp'])
        self.packages_leftbox.append(self.option_packages['graphicx'])
        self.packages_leftbox.append(self.option_packages['color'])
        self.packages_leftbox.append(self.option_packages['xcolor'])
        self.packages_leftbox.append(self.option_packages['url'])

        self.packages_rightbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.packages_rightbox.set_size_request(348, -1)
        self.packages_rightbox.append(self.option_packages['hyperref'])
        self.packages_rightbox.append(self.option_packages['theorem'])
        self.packages_rightbox.append(self.option_packages['listings'])
        self.packages_rightbox.append(self.option_packages['glossaries'])
        self.packages_rightbox.append(self.option_packages['parskip'])

        self.packages_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.packages_box.get_style_context().add_class('packages')
        self.packages_box.append(self.packages_leftbox)
        self.packages_box.append(self.packages_rightbox)

        self.packages_tooltip = Gtk.Label.new('')
        self.packages_tooltip_data = dict()
        self.packages_tooltip_data['ams'] = _('<b>AMS packages:</b> provide mathematical symbols, math-related environments, …') + ' (' + _('recommended') + ')'
        self.packages_tooltip_data['textcomp'] = '<b>textcomp:</b> ' + _('contains symbols to be used in textmode.') + ' (' + _('recommended') + ')'
        self.packages_tooltip_data['graphicx'] = '<b>graphicx:</b> ' + _('include graphics in your document.') + ' (' + _('recommended') + ')'
        self.packages_tooltip_data['color'] = '<b>color:</b> ' + _('foreground and background color.') + ' (' + _('recommended') + ')'
        self.packages_tooltip_data['xcolor'] = '<b>xcolor:</b> ' + _('enables colored text.') + ' (' + _('recommended') + ')'
        self.packages_tooltip_data['url'] = '<b>url:</b> ' + _('type urls with the \\url{..} command without escaping them.') + ' (' + _('recommended') + ')'
        self.packages_tooltip_data['hyperref'] = '<b>hyperref:</b> ' + _('create hyperlinks within your document.')
        self.packages_tooltip_data['theorem'] = '<b>theorem:</b> ' + _('define theorem environments (like "definition", "lemma", …) with custom styling.')
        self.packages_tooltip_data['listings'] = '<b>listings:</b> ' + _('provides the \\listing environment for embedding programming code.')
        self.packages_tooltip_data['glossaries'] = '<b>glossaries:</b> ' + _('create a glossary for your document.')
        self.packages_tooltip_data['parskip'] = '<b>parskip:</b> ' + _('paragraphs without indentation.')
        self.packages_tooltip.set_markup(' ')
        self.packages_tooltip.set_xalign(0)
        self.packages_tooltip.set_wrap(True)
        self.packages_tooltip.set_margin_top(12)
        self.packages_tooltip.set_margin_end(18)
        self.packages_tooltip.set_size_request(714, -1)

        self.form = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.form.append(self.subheader_title)
        self.form.append(self.title_entry)
        self.form.append(self.document_properties_hbox)
        self.form.append(self.subheader_language)
        self.form.append(self.language_box)
        self.form.append(self.language_description)
        self.form.append(self.subheader_packages)
        self.form.append(self.packages_box)
        self.form.append(self.packages_tooltip)

        self.content = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.content.append(self.form)

        self.append(self.header)
        self.append(self.content)


