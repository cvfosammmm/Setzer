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
from gi.repository import GLib
from gi.repository import GdkPixbuf

from setzer.dialogs.document_wizard.pages.page import Page, PageView
from setzer.app.service_locator import ServiceLocator

import os
import _thread as thread


class BeamerSettingsPage(Page):

    def __init__(self, current_values):
        self.current_values = current_values
        self.view = BeamerSettingsPageView()

        self.image_loading_lock = thread.allocate_lock()
        thread.start_new_thread(self.load_beamer_images, ())

    def observe_view(self):
        self.image_loading_lock.acquire()
        self.image_loading_lock.release()

        def row_selected(box, row, user_data=None):
            child_name = row.get_child().get_text()
            self.current_values['beamer']['theme'] = child_name
            for i in range(0, 2):
                image_box = self.view.preview_image_boxes[child_name][i]
                if image_box.get_center_widget() == None:
                    image_box.set_center_widget(self.view.preview_images[child_name][i])
                    image_box.show_all()
            self.view.preview_stack.set_transition_type(Gtk.StackTransitionType.NONE)
            self.view.preview_stack.set_visible_child_name(child_name + '_0')

            button = self.view.preview_buttons[child_name][0]
            button.set_image(self.view.preview_button_images[child_name][0])
            button = self.view.preview_buttons[child_name][1]
            button.set_image(self.view.preview_button_images[child_name][1])
            self.view.preview_button_stack.set_visible_child_name(child_name)

        def option_toggled(button, option_name):
            self.current_values['beamer']['option_' + option_name] = button.get_active()

        def preview_button_clicked(button, theme_name, number):
            stack = self.view.preview_stack
            if number == 0:
                stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
            elif number == 1:
                stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
            stack.set_visible_child_name(theme_name + '_' + str(number))

        self.view.themes_list.connect('row-selected', row_selected)
        self.view.option_show_navigation.connect('toggled', option_toggled, 'show_navigation')
        self.view.option_top_align.connect('toggled', option_toggled, 'top_align')
        for name in self.view.theme_names:
            for i in range(0, 2):
                button = self.view.preview_buttons[name][i]
                button.set_can_focus(False)
                button.connect('clicked', preview_button_clicked, name, i)

    def load_beamer_images(self):
        with self.image_loading_lock:
            for name in self.view.theme_names:
                for i in range(0, 2):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(ServiceLocator.get_resources_path(), 'document_wizard', 'beamerpreview_' + name + '_page_' + str(i) + '.png'), 346, 260, False)
                    image = Gtk.Image.new_from_pixbuf(pixbuf)
                    self.view.preview_images[name].append(image)
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(ServiceLocator.get_resources_path(), 'document_wizard', 'beamerpreview_' + name + '_page_' + str(i) + '.png'), 100, 75, False)
                    image = Gtk.Image.new_from_pixbuf(pixbuf)
                    self.view.preview_button_images[name].append(image)
            self.view.preview_stack.show_all()

    def load_presets(self, presets):
        try:
            row = self.view.themes_list_rows[presets['beamer']['theme']]
        except TypeError:
            row = self.view.themes_list_rows[self.current_values['beamer']['theme']]
        except KeyError:
            row = self.view.themes_list_rows[self.current_values['beamer']['theme']]
        self.view.themes_list.select_row(row)

        for setter_function, value_name in [
            (self.view.option_show_navigation.set_active, 'option_show_navigation'),
            (self.view.option_top_align.set_active, 'option_top_align')
        ]:
            try:
                value = presets['beamer'][value_name]
            except TypeError:
                value = self.current_values['beamer'][value_name]
            setter_function(value)

    def on_activation(self):
        GLib.idle_add(self.view.themes_list.get_selected_row().grab_focus)


class BeamerSettingsPageView(PageView):

    def __init__(self):
        PageView.__init__(self)
            
        self.header.set_text(_('Beamer settings'))
        self.headerbar_subtitle = _('Step') + ' 2: ' + _('Beamer settings')
        self.content = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.form = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        
        self.theme_names = ['Warsaw', 'Malmoe', 'Luebeck', 'Copenhagen', 'Szeged', 'Singapore', 'Frankfurt', 'Darmstadt', 'Dresden', 'Ilmenau', 'Berlin', 'Hannover', 'Marburg', 'Goettingen', 'PaloAlto', 'Berkeley', 'Montpellier', 'JuanLesPins', 'Antibes', 'Rochester', 'Pittsburgh', 'EastLansing', 'CambridgeUS', 'AnnArbor', 'Madrid', 'Boadilla', 'Bergen', 'default']

        self.subheader_themes = Gtk.Label(_('Themes'))
        self.subheader_themes.get_style_context().add_class('document-wizard-subheader')
        self.subheader_themes.set_xalign(0)

        self.themes_list_scrolled_window = Gtk.ScrolledWindow()
        self.themes_list_scrolled_window.set_size_request(348, 230)
        self.themes_list_scrolled_window.get_style_context().add_class('document-wizard-scrolledwindow')
        self.themes_list = Gtk.ListBox()
        self.themes_list.set_can_focus(True)
        self.themes_list.set_size_request(346, -1)
        self.themes_list_rows = dict()
        for name in self.theme_names:
            label = Gtk.Label(name)
            label.set_xalign(0)
            self.themes_list.prepend(label)
        for row in self.themes_list.get_children():
            self.themes_list_rows[row.get_child().get_text()] = row
        self.themes_list.set_margin_right(0)
        self.themes_list.set_vexpand(False)
        self.themes_list.get_style_context().add_class('document-wizard-list2')
        self.themes_list_scrolled_window.add(self.themes_list)
        
        self.subheader_options = Gtk.Label(_('Options'))
        self.subheader_options.get_style_context().add_class('document-wizard-subheader')
        self.subheader_options.set_margin_top(18)
        self.subheader_options.set_xalign(0)
        
        self.option_show_navigation = Gtk.CheckButton.new_with_label(_('Show navigation buttons'))
        self.option_top_align = Gtk.CheckButton.new_with_label(_('Align content to the top of pages'))
        self.option_top_align.get_style_context().add_class('has-desc')
        self.option_top_align_desc = Gtk.Label(_('("t" option, it\'s centered by default)'))
        self.option_top_align_desc.get_style_context().add_class('document-wizard-option-desc')
        self.option_top_align_desc.set_xalign(0)
        
        self.preview = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.preview_stack_wrapper = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.preview_stack_wrapper.get_style_context().add_class('document-wizard-beamer-preview-stack-wrapper')
        self.preview_stack = Gtk.Stack()
        self.preview_button_stack = Gtk.Stack()
        self.preview_button_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.preview_images = dict()
        self.preview_image_boxes = dict()
        self.preview_buttons = dict()
        self.preview_button_widgets = dict()
        self.preview_button_images = dict()
        for name in self.theme_names:
            self.preview_images[name] = list()
            self.preview_image_boxes[name] = list()
            self.preview_buttons[name] = list()
            button_box =  Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
            button_box.get_style_context().add_class('document-wizard-beamer-preview-buttons')
            self.preview_button_widgets[name] = button_box
            self.preview_button_stack.add_named(button_box, name)
            for i in range(0, 2):
                image_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
                self.preview_image_boxes[name].append(image_box)
                self.preview_stack.add_named(image_box, name + '_' + str(i))
                button = Gtk.Button()
                button.set_margin_end(12)
                button.set_margin_top(12)
                button.set_relief(Gtk.ReliefStyle.NONE)
                self.preview_buttons[name].append(button)
                self.preview_button_images[name] = list()
                self.preview_button_widgets[name].pack_start(button, False, False, 0)
        self.preview_stack_wrapper.pack_start(self.preview_stack, False, False, 0)
        self.preview.pack_start(self.preview_stack_wrapper, False, False, 0)
        self.preview.pack_start(self.preview_button_stack, False, False, 0)
        self.preview.set_margin_top(30)
        self.preview.set_margin_start(18)
        self.preview.set_margin_end(18)

        self.pack_start(self.header, False, False, 0)
        self.form.pack_start(self.subheader_themes, False, False, 0)
        self.form.pack_start(self.themes_list_scrolled_window, False, False, 0)
        self.form.pack_start(self.subheader_options, False, False, 0)
        self.form.pack_start(self.option_show_navigation, False, False, 0)
        self.form.pack_start(self.option_top_align, False, False, 0)
        self.form.pack_start(self.option_top_align_desc, False, False, 0)
        self.content.pack_start(self.form, False, False, 0)
        self.content.pack_start(self.preview, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()


