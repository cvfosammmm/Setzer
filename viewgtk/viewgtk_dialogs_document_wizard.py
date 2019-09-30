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
from gi.repository import Gtk, GLib
from gi.repository import Gdk, GdkPixbuf

import os

import helpers.helpers as helpers


class DocumentWizardView(object):
    ''' Create document templates for users to build on. '''

    def __init__(self, main_window):
        builder = Gtk.Builder.new_from_string('<?xml version="1.0" encoding="UTF-8"?><interface><object class="GtkDialog" id="dialog"><property name="use-header-bar">1</property></object></interface>', -1)

        self.dialog = builder.get_object('dialog')
        self.dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(main_window)
        self.dialog.set_destroy_with_parent(True)
        self.dialog.set_default_size(750, 500)
        self.dialog.set_can_focus(False)
        self.topbox = self.dialog.get_content_area()
        self.topbox.set_border_width(0)
        self.topbox.set_size_request(750, 450)
        self.center_box = Gtk.HBox()
        self.pages = list()
        
        self.create_headerbar()
        self.create_pages()

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.center_box.set_center_widget(self.notebook)
        self.topbox.pack_start(self.center_box, True, True, 0)
        self.add_pages()
        self.center_box.show_all()

    def create_headerbar(self):
        self.headerbar = self.dialog.get_header_bar()
        self.headerbar.set_show_close_button(False)
        self.headerbar.set_title('Create a template document')
        self.headerbar.set_subtitle('')

        self.cancel_button = self.dialog.add_button('_Cancel', Gtk.ResponseType.CANCEL)
        self.cancel_button.set_can_focus(False)
        self.back_button = Gtk.Button.new_with_mnemonic('_Back')
        self.back_button.set_can_focus(False)
        
        self.next_button = Gtk.Button.new_with_mnemonic('_Next')
        self.next_button.set_can_focus(False)
        self.next_button.get_style_context().add_class('suggested-action')
        self.create_button = self.dialog.add_button('_Create', Gtk.ResponseType.APPLY)
        self.create_button.set_can_focus(False)
        self.create_button.get_style_context().add_class('suggested-action')
        
        self.headerbar.pack_start(self.back_button)
        self.headerbar.pack_end(self.next_button)
        self.headerbar.show_all()

    def create_pages(self):
        self.document_class_page = DocumentWizardDocumentClassPageView()
        self.article_settings_page = DocumentWizardArticleSettingsPageView()
        self.report_settings_page = DocumentWizardReportSettingsPageView()
        self.book_settings_page = DocumentWizardBookSettingsPageView()
        self.letter_settings_page = DocumentWizardLetterSettingsPageView()
        self.beamer_settings_page = DocumentWizardBeamerSettingsPageView()
        self.general_settings_page = DocumentWizardGeneralSettingsPageView()

    def add_pages(self):
        self.notebook.append_page(self.document_class_page)
        self.notebook.append_page(self.article_settings_page)
        self.notebook.append_page(self.report_settings_page)
        self.notebook.append_page(self.book_settings_page)
        self.notebook.append_page(self.letter_settings_page)
        self.notebook.append_page(self.beamer_settings_page)
        self.notebook.append_page(self.general_settings_page)

        self.pages.append(self.document_class_page)
        self.pages.append(self.article_settings_page)
        self.pages.append(self.report_settings_page)
        self.pages.append(self.book_settings_page)
        self.pages.append(self.letter_settings_page)
        self.pages.append(self.beamer_settings_page)
        self.pages.append(self.general_settings_page)

    def run(self):
        return self.dialog.run()
        
    def __del__(self):
        self.dialog.destroy()


class DocumentWizardPageView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.get_style_context().add_class('document-wizard-page')

        self.set_margin_start(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)

        self.header = Gtk.Label()
        self.header.set_xalign(0)
        self.header.set_margin_bottom(12)
        self.header.get_style_context().add_class('document-wizard-header')
        
        self.headerbar_subtitle = ''


class DocumentWizardDocumentClassPageView(DocumentWizardPageView):

    def __init__(self):
        DocumentWizardPageView.__init__(self)
            
        self.header.set_text('Choose a document class')
        self.headerbar_subtitle = 'Step 1: Choose document class'
        self.content = Gtk.HBox()
        
        self.list = Gtk.ListBox()
        self.list.set_can_focus(True)
        self.list.set_size_request(348, -1)
        self.list_rows = dict()
        for name in ['Beamer', 'Letter', 'Book', 'Report', 'Article']:
            label = Gtk.Label(name)
            label.set_xalign(0)
            self.list.prepend(label)
        for row in self.list.get_children():
            self.list_rows[row.get_child().get_text().lower()] = row
            row.set_can_focus(True)
        self.list.set_margin_right(0)
        self.list.set_vexpand(False)
        self.list.get_style_context().add_class('document-wizard-list1')
        
        self.preview_container = Gtk.Stack()
        self.preview_container.set_size_request(366, -1)
        self.preview_data = list()
        self.preview_data.append({'name': 'article', 'image': 'article1.svg', 'text': '<b>Article:</b>  For articles in scientific journals, term\npapers, handouts, short reports, ...\n\nThis class on its own is pretty simplistic and\nis often used as a starting point for more\ncustom layouts.'})
        self.preview_data.append({'name': 'book', 'image': 'book1.svg', 'text': '<b>Book:</b>  For actual books containing many chapters\nand sections.'})
        self.preview_data.append({'name': 'report', 'image': 'report1.svg', 'text': '<b>Report:</b>  For longer reports and articles containing\nmore than one chapter, small books, thesis.'})
        self.preview_data.append({'name': 'letter', 'image': 'letter1.svg', 'text': '<b>Letter:</b>  For writing letters.'})
        self.preview_data.append({'name': 'beamer', 'image': 'beamer1.svg', 'text': '<b>Beamer:</b>  A class for making presentation slides\nwith LaTeX.\n\nThere are many predefined presentation styles.'})
        for item in self.preview_data:
            box = Gtk.VBox()
            image = Gtk.Image.new_from_file(os.path.dirname(__file__) + '/../resources/images/documentwizard/' + item['image'])
            image.set_margin_bottom(6)
            label = Gtk.Label()
            label.set_markup(item['text'])
            label.set_xalign(0)
            label.set_margin_start(19)
            box.pack_start(image, False, False, 0)
            box.pack_start(label, False, False, 0)
            self.preview_container.add_named(box, item['name'])
        
        self.pack_start(self.header, False, False, 0)
        self.content.pack_start(self.list, False, False, 0)
        self.content.pack_start(self.preview_container, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()

    def list_grab_focus(self):
        self.list.get_selected_row().grab_focus()


class DocumentWizardDocumentSettingsPageView(DocumentWizardPageView):

    def __init__(self):
        DocumentWizardPageView.__init__(self)

        self.headerbar_subtitle = 'Step 2'
        self.content = Gtk.HBox()
        self.left_content = Gtk.VBox()

        self.subheader_page_format = Gtk.Label('Page format')
        self.subheader_page_format.get_style_context().add_class('document-wizard-subheader')
        self.subheader_page_format.set_xalign(0)

        self.page_format_list = Gtk.ListBox()
        self.page_format_list.set_can_focus(True)
        self.page_format_list.set_size_request(348, -1)
        self.page_format_list_rows = dict()
        for name in ['B5', 'A5', 'A4', 'US Legal', 'US Letter']:
            label = Gtk.Label(name)
            label.set_xalign(0)
            self.page_format_list.prepend(label)
        for row in self.page_format_list.get_children():
            self.page_format_list_rows[row.get_child().get_text()] = row
        self.page_format_list.set_margin_right(0)
        self.page_format_list.set_vexpand(False)
        self.page_format_list.get_style_context().add_class('document-wizard-list1')
        
        self.subheader_font_size = Gtk.Label('Font size')
        self.subheader_font_size.get_style_context().add_class('document-wizard-subheader')
        self.subheader_font_size.set_xalign(0)
        self.subheader_font_size.set_margin_top(18)

        self.font_size_entry = Gtk.HScale.new_with_range(6, 18, 1)
        
    def list_grab_focus(self):
        self.page_format_list.get_selected_row().grab_focus()


class DocumentWizardArticleSettingsPageView(DocumentWizardDocumentSettingsPageView):

    def __init__(self):
        DocumentWizardDocumentSettingsPageView.__init__(self)
            
        self.header.set_text('Article settings')

        self.subheader_options = Gtk.Label('Options')
        self.subheader_options.get_style_context().add_class('document-wizard-subheader')
        self.subheader_options.set_xalign(0)
        self.subheader_options.set_margin_top(18)

        self.option_twocolumn = Gtk.CheckButton.new_with_label('Two-column layout')

        self.pack_start(self.header, False, False, 0)
        self.left_content.pack_start(self.subheader_page_format, False, False, 0)
        self.left_content.pack_start(self.page_format_list, False, False, 0)
        self.left_content.pack_start(self.subheader_font_size, False, False, 0)
        self.left_content.pack_start(self.font_size_entry, False, False, 0)
        self.left_content.pack_start(self.subheader_options, False, False, 0)
        self.left_content.pack_start(self.option_twocolumn, False, False, 0)
        self.content.pack_start(self.left_content, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()


class DocumentWizardReportSettingsPageView(DocumentWizardDocumentSettingsPageView):

    def __init__(self):
        DocumentWizardDocumentSettingsPageView.__init__(self)
            
        self.header.set_text('Report settings')

        self.subheader_options = Gtk.Label('Options')
        self.subheader_options.get_style_context().add_class('document-wizard-subheader')
        self.subheader_options.set_xalign(0)
        self.subheader_options.set_margin_top(18)

        self.option_twocolumn = Gtk.CheckButton.new_with_label('Two-column layout')

        self.pack_start(self.header, False, False, 0)
        self.left_content.pack_start(self.subheader_page_format, False, False, 0)
        self.left_content.pack_start(self.page_format_list, False, False, 0)
        self.left_content.pack_start(self.subheader_font_size, False, False, 0)
        self.left_content.pack_start(self.font_size_entry, False, False, 0)
        self.left_content.pack_start(self.subheader_options, False, False, 0)
        self.left_content.pack_start(self.option_twocolumn, False, False, 0)
        self.content.pack_start(self.left_content, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()


class DocumentWizardBookSettingsPageView(DocumentWizardDocumentSettingsPageView):

    def __init__(self):
        DocumentWizardDocumentSettingsPageView.__init__(self)
            
        self.header.set_text('Book settings')

        self.subheader_options = Gtk.Label('Options')
        self.subheader_options.get_style_context().add_class('document-wizard-subheader')
        self.subheader_options.set_xalign(0)
        self.subheader_options.set_margin_top(18)

        self.option_twocolumn = Gtk.CheckButton.new_with_label('Two-column layout')

        self.pack_start(self.header, False, False, 0)
        self.left_content.pack_start(self.subheader_page_format, False, False, 0)
        self.left_content.pack_start(self.page_format_list, False, False, 0)
        self.left_content.pack_start(self.subheader_font_size, False, False, 0)
        self.left_content.pack_start(self.font_size_entry, False, False, 0)
        self.left_content.pack_start(self.subheader_options, False, False, 0)
        self.left_content.pack_start(self.option_twocolumn, False, False, 0)
        self.content.pack_start(self.left_content, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()


class DocumentWizardLetterSettingsPageView(DocumentWizardDocumentSettingsPageView):

    def __init__(self):
        DocumentWizardDocumentSettingsPageView.__init__(self)
            
        self.header.set_text('Letter settings')

        self.pack_start(self.header, False, False, 0)
        self.left_content.pack_start(self.subheader_page_format, False, False, 0)
        self.left_content.pack_start(self.page_format_list, False, False, 0)
        self.left_content.pack_start(self.subheader_font_size, False, False, 0)
        self.left_content.pack_start(self.font_size_entry, False, False, 0)
        self.content.pack_start(self.left_content, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()


class DocumentWizardBeamerSettingsPageView(DocumentWizardPageView):

    def __init__(self):
        DocumentWizardPageView.__init__(self)
            
        self.header.set_text('Beamer settings')
        self.headerbar_subtitle = 'Step 2: Beamer settings'
        self.content = Gtk.HBox()
        self.form = Gtk.VBox()
        
        self.theme_names = ['Warsaw', 'Malmoe', 'Luebeck', 'Copenhagen', 'Szeged', 'Singapore', 'Frankfurt', 'Darmstadt', 'Dresden', 'Ilmenau', 'Berlin', 'Hannover', 'Marburg', 'Goettingen', 'PaloAlto', 'Berkeley', 'Montpellier', 'JuanLesPins', 'Antibes', 'Rochester', 'Pittsburgh', 'EastLansing', 'CambridgeUS', 'AnnArbor', 'Madrid', 'Boadilla', 'Bergen', 'Default']

        self.subheader_themes = Gtk.Label('Themes')
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
        
        self.subheader_options = Gtk.Label('Options')
        self.subheader_options.get_style_context().add_class('document-wizard-subheader')
        self.subheader_options.set_margin_top(18)
        self.subheader_options.set_xalign(0)
        
        self.option_show_navigation = Gtk.CheckButton.new_with_label('Show navigation buttons')
        self.option_top_align = Gtk.CheckButton.new_with_label('Align content to the top of pages')
        self.option_top_align.get_style_context().add_class('has-desc')
        self.option_top_align_desc = Gtk.Label('("t" option, it\'s centered by default)')
        self.option_top_align_desc.get_style_context().add_class('document-wizard-option-desc')
        self.option_top_align_desc.set_xalign(0)
        
        self.preview = Gtk.VBox()
        self.preview_stack_wrapper = Gtk.VBox()
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
            button_box =  Gtk.HBox()
            button_box.get_style_context().add_class('document-wizard-beamer-preview-buttons')
            self.preview_button_widgets[name] = button_box
            self.preview_button_stack.add_named(button_box, name)
            for i in range(0, 2):
                image_box = Gtk.HBox()
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

    def list_grab_focus(self):
        self.themes_list.get_selected_row().grab_focus()


class DocumentWizardGeneralSettingsPageView(DocumentWizardPageView):

    def __init__(self):
        DocumentWizardPageView.__init__(self)
            
        self.header.set_text('General document settings')
        self.headerbar_subtitle = 'Step 3: General document settings'
        self.content = Gtk.HBox()
        self.form = Gtk.VBox()

        self.subheader_title = Gtk.Label('Title')
        self.subheader_title.get_style_context().add_class('document-wizard-subheader')
        self.subheader_title.set_xalign(0)
        self.title_entry = Gtk.Entry()
        self.title_entry.set_margin_right(250)
        self.subheader_author = Gtk.Label('Author')
        self.subheader_author.get_style_context().add_class('document-wizard-subheader')
        self.subheader_author.set_xalign(0)
        self.author_entry = Gtk.Entry()
        self.author_entry.set_margin_right(100)
        self.author_box = Gtk.VBox()
        self.author_box.pack_start(self.subheader_author, False, False, 0)
        self.author_box.pack_start(self.author_entry, False, False, 0)
        self.author_box.set_size_request(348, -1)
        self.subheader_date = Gtk.Label('Date')
        self.subheader_date.get_style_context().add_class('document-wizard-subheader')
        self.subheader_date.set_xalign(0)
        self.date_entry = Gtk.Entry()
        self.date_entry.set_margin_right(100)
        self.date_box = Gtk.VBox()
        self.date_box.pack_start(self.subheader_date, False, False, 0)
        self.date_box.pack_start(self.date_entry, False, False, 0)
        self.date_box.set_size_request(348, -1)
        self.document_properties_hbox = Gtk.HBox()
        self.document_properties_hbox.set_margin_top(18)
        self.document_properties_hbox.pack_start(self.author_box, False, False, 0)
        self.document_properties_hbox.pack_start(self.date_box, False, False, 0)

        self.subheader_packages = Gtk.Label('Packages')
        self.subheader_packages.get_style_context().add_class('document-wizard-subheader')
        self.subheader_packages.set_margin_top(18)
        self.subheader_packages.set_xalign(0)
        
        self.packages_box = Gtk.HBox()
        self.packages_leftbox = Gtk.VBox()
        self.packages_leftbox.set_size_request(348, -1)
        self.packages_rightbox = Gtk.VBox()
        self.packages_rightbox.set_size_request(348, -1)
        self.option_packages = dict()
        self.option_packages['ams'] = Gtk.CheckButton.new_with_label('AMS math packages')
        self.option_packages['textcomp'] = Gtk.CheckButton.new_with_label('textcomp')
        self.option_packages['graphicx'] = Gtk.CheckButton.new_with_label('graphicx')
        self.option_packages['xcolor'] = Gtk.CheckButton.new_with_label('xcolor')
        self.option_packages['url'] = Gtk.CheckButton.new_with_label('url')
        self.option_packages['hyperref'] = Gtk.CheckButton.new_with_label('hyperref')
        self.option_packages['theorem'] = Gtk.CheckButton.new_with_label('theorem')
        self.option_packages['listings'] = Gtk.CheckButton.new_with_label('listings')
        self.option_packages['glossaries'] = Gtk.CheckButton.new_with_label('glossaries')
        self.option_packages['parskip'] = Gtk.CheckButton.new_with_label('parskip')
        self.packages_leftbox.pack_start(self.option_packages['ams'], False, False, 0)
        self.packages_leftbox.pack_start(self.option_packages['textcomp'], False, False, 0)
        self.packages_leftbox.pack_start(self.option_packages['graphicx'], False, False, 0)
        self.packages_leftbox.pack_start(self.option_packages['xcolor'], False, False, 0)
        self.packages_leftbox.pack_start(self.option_packages['url'], False, False, 0)
        self.packages_rightbox.pack_start(self.option_packages['hyperref'], False, False, 0)
        self.packages_rightbox.pack_start(self.option_packages['theorem'], False, False, 0)
        self.packages_rightbox.pack_start(self.option_packages['listings'], False, False, 0)
        self.packages_rightbox.pack_start(self.option_packages['glossaries'], False, False, 0)
        self.packages_rightbox.pack_start(self.option_packages['parskip'], False, False, 0)
        self.packages_box.pack_start(self.packages_leftbox, False, False, 0)
        self.packages_box.pack_start(self.packages_rightbox, False, False, 0)
        
        self.packages_tooltip = Gtk.Label()
        self.packages_tooltip_data = dict()
        self.packages_tooltip_data['ams'] = '<b>AMS packages:</b> provide mathematical symbols, math-related environments, ... (recommended)'
        self.packages_tooltip_data['textcomp'] = '<b>textcomp:</b> contains symbols to be used in textmode. (recommended)'
        self.packages_tooltip_data['graphicx'] = '<b>graphicx:</b> include graphics in your document. (recommended)'
        self.packages_tooltip_data['xcolor'] = '<b>xcolor:</b> enables colored text. (recommended)'
        self.packages_tooltip_data['url'] = '<b>url:</b> type urls with the \\url{..} command without escaping them. (recommended)'
        self.packages_tooltip_data['hyperref'] = '<b>hyperref:</b> create hyperlinks within your document.'
        self.packages_tooltip_data['theorem'] = '<b>theorem:</b> define theorem environments (like "definition", "lemma", ...) with custom styling.'
        self.packages_tooltip_data['listings'] = '<b>listings:</b> provides the \\listing environment for embedding programming code.'
        self.packages_tooltip_data['glossaries'] = '<b>glossaries:</b> create a glossary for your document.'
        self.packages_tooltip_data['parskip'] = '<b>parskip:</b> paragraphs without indentation.'
        self.packages_tooltip.set_markup(' ')
        self.packages_tooltip.set_xalign(0)
        self.packages_tooltip.set_margin_top(12)

        self.pack_start(self.header, False, False, 0)
        self.form.pack_start(self.subheader_title, False, False, 0)
        self.form.pack_start(self.title_entry, False, False, 0)
        self.form.pack_start(self.document_properties_hbox, False, False, 0)
        self.form.pack_start(self.subheader_packages, False, False, 0)
        self.form.pack_start(self.packages_box, False, False, 0)
        self.form.pack_start(self.packages_tooltip, False, False, 0)
        self.content.pack_start(self.form, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()


