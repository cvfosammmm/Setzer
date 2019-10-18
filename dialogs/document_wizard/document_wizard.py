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
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GdkPixbuf
from gi.repository import Gdk

from dialogs.dialog import Dialog
import dialogs.document_wizard.document_wizard_viewgtk as viewgtk

import _thread as thread
import pickle
import os


class DocumentWizard(Dialog):
    ''' Create document templates for users to build on. '''

    def __init__(self, main_window, workspace, settings):
        self.main_window = main_window
        self.workspace = workspace
        self.settings = settings
        self.page_formats = {'US Letter': 'letterpaper', 'US Legal': 'legalpaper', 'A4': 'a4paper', 'A5': 'a5paper', 'B5': 'b5paper'}

        self.view = viewgtk.DocumentWizardView(self.main_window)
        self.image_loading_lock = thread.allocate_lock()
        thread.start_new_thread(self.load_beamer_images, ())

    def run(self, document):
        self.image_loading_lock.acquire()
        self.image_loading_lock.release()

        self.document = document
        self.presets = None
        self.current_page = None
        self.init_current_values()
        self.setup()

        self.load_presets()
        self.goto_page(0)
        response = self.view.run()

        if response == Gtk.ResponseType.APPLY:
            self.save_presets()
            self.insert_template()

        self.view.dialog.hide()

    def init_current_values(self):
        self.current_values = dict()
        self.current_values['document_class'] = 'article'
        self.current_values['title'] = ''
        self.current_values['author'] = ''
        self.current_values['date'] = '\\today'
        self.current_values['packages'] = dict()
        self.current_values['packages']['ams'] = True
        self.current_values['packages']['graphicx'] = True
        self.current_values['packages']['xcolor'] = True
        self.current_values['packages']['url'] = True
        self.current_values['packages']['theorem'] = False
        self.current_values['packages']['textcomp'] = True
        self.current_values['packages']['listings'] = False
        self.current_values['packages']['hyperref'] = False
        self.current_values['packages']['glossaries'] = False
        self.current_values['packages']['parskip'] = True
        self.current_values['article'] = dict()
        self.current_values['article']['page_format'] = 'US Letter'
        self.current_values['article']['font_size'] = 11
        self.current_values['article']['option_twocolumn'] = False
        self.current_values['report'] = dict()
        self.current_values['report']['page_format'] = 'US Letter'
        self.current_values['report']['font_size'] = 11
        self.current_values['report']['option_twocolumn'] = False
        self.current_values['book'] = dict()
        self.current_values['book']['page_format'] = 'US Letter'
        self.current_values['book']['font_size'] = 11
        self.current_values['book']['option_twocolumn'] = False
        self.current_values['letter'] = dict()
        self.current_values['letter']['page_format'] = 'US Letter'
        self.current_values['letter']['font_size'] = 11
        self.current_values['beamer'] = dict()
        self.current_values['beamer']['theme'] = 'Default'
        self.current_values['beamer']['option_show_navigation'] = True
        self.current_values['beamer']['option_top_align'] = True
    
    def setup(self):
        self.view.dialog.connect('key-press-event', self.on_keypress)
        self.observe_document_class_page()
        self.observe_article_settings_page()
        self.observe_report_settings_page()
        self.observe_book_settings_page()
        self.observe_letter_settings_page()
        self.observe_beamer_settings_page()
        self.observe_general_settings_page()
        self.view.next_button.connect('clicked', self.goto_page_next)
        self.view.back_button.connect('clicked', self.goto_page_prev)

    def load_beamer_images(self):
        self.image_loading_lock.acquire()
        page = self.view.beamer_settings_page
        for name in self.view.beamer_settings_page.theme_names:
            for i in range(0, 2):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.dirname(__file__) + '/../../resources/images/documentwizard/beamerpreview_' + name + '_page_' + str(i) + '.png', 346, 260, False)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                page.preview_images[name].append(image)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.dirname(__file__) + '/../../resources/images/documentwizard/beamerpreview_' + name + '_page_' + str(i) + '.png', 100, 75, False)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                page.preview_button_images[name].append(image)
        self.view.beamer_settings_page.preview_stack.show_all()
        self.image_loading_lock.release()

    def load_presets(self):
        if self.presets == None:
            presets = self.settings.get_value('app_document_wizard', 'presets')
            if presets == None: return
            else: self.presets = pickle.loads(presets)

        try:
            row = self.view.document_class_page.list_rows[self.presets['document_class']]
        except KeyError:
            row = self.view.document_class_page.list_rows[self.current_values['document_class']]
        self.view.document_class_page.list.select_row(row)

        try:
            row = self.view.beamer_settings_page.themes_list_rows[self.presets['beamer']['theme']]
        except KeyError:
            row = self.view.beamer_settings_page.themes_list_rows[self.current_values['beamer']['theme']]
        self.view.beamer_settings_page.themes_list.select_row(row)

        try:
            is_active = self.presets['beamer']['option_show_navigation']
        except KeyError:
            is_active = self.current_values['beamer']['option_show_navigation']
        self.view.beamer_settings_page.option_show_navigation.set_active(is_active)

        try:
            is_active = self.presets['beamer']['option_top_align']
        except KeyError:
            is_active = self.current_values['beamer']['option_top_align']
        self.view.beamer_settings_page.option_top_align.set_active(is_active)
        
        for no, page_class in [(1, 'article'), (2, 'report'), (3, 'book'), (4, 'letter')]:
            try:
                row = self.view.pages[no].page_format_list_rows[self.presets[page_class]['page_format']]
            except KeyError:
                row = self.view.pages[no].page_format_list_rows[self.current_values[page_class]['page_format']]
            self.view.pages[no].page_format_list.select_row(row)

        for no, page_class in [(1, 'article'), (2, 'report'), (3, 'book'), (4, 'letter')]:
            try:
                value = self.presets[page_class]['font_size']
            except KeyError:
                value = self.current_values[page_class]['font_size']
            self.view.pages[no].font_size_entry.set_value(value)

        for no, page_class in [(1, 'article'), (2, 'report'), (3, 'book')]:
            try:
                is_active = self.presets[page_class]['option_twocolumn']
            except KeyError:
                is_active = self.current_values[page_class]['option_twocolumn']
            self.view.pages[no].option_twocolumn.set_active(is_active)

        try:
            text = self.presets['author']
        except KeyError:
            text = self.current_values['author']
        self.view.general_settings_page.author_entry.set_text(text)
        self.view.general_settings_page.title_entry.set_text('')
        self.view.general_settings_page.date_entry.set_text('\\today')

        for name, option in self.view.general_settings_page.option_packages.items():
            try:
                is_active = self.presets['packages'][name]
            except KeyError:
                is_active = self.current_values['packages'][name]
            option.set_active(is_active)

    def save_presets(self):
        self.presets = dict()
        self.presets['document_class'] = self.current_values['document_class']
        self.presets['author'] = self.current_values['author']
        self.presets['packages'] = self.current_values['packages']
        
        self.presets['beamer'] = dict()
        self.presets['beamer']['theme'] = self.current_values['beamer']['theme']
        self.presets['beamer']['option_show_navigation'] = self.current_values['beamer']['option_show_navigation']
        self.presets['beamer']['option_top_align'] = self.current_values['beamer']['option_top_align']
        
        self.presets['article'] = dict()
        self.presets['article']['page_format'] = self.current_values['article']['page_format']
        self.presets['article']['font_size'] = self.current_values['article']['font_size']
        self.presets['article']['option_twocolumn'] = self.current_values['article']['option_twocolumn']
        
        self.presets['report'] = dict()
        self.presets['report']['page_format'] = self.current_values['report']['page_format']
        self.presets['report']['font_size'] = self.current_values['report']['font_size']
        self.presets['report']['option_twocolumn'] = self.current_values['report']['option_twocolumn']
        
        self.presets['book'] = dict()
        self.presets['book']['page_format'] = self.current_values['book']['page_format']
        self.presets['book']['font_size'] = self.current_values['book']['font_size']
        self.presets['book']['option_twocolumn'] = self.current_values['book']['option_twocolumn']
        
        self.presets['letter'] = dict()
        self.presets['letter']['page_format'] = self.current_values['letter']['page_format']
        self.presets['letter']['font_size'] = self.current_values['letter']['font_size']
        
        self.settings.set_value('app_document_wizard', 'presets', pickle.dumps(self.presets))

    def goto_page_next(self, button=None, data=None):
        if self.current_page == 0:
            if self.current_values['document_class'] == 'article': self.goto_page(1)
            elif self.current_values['document_class'] == 'report': self.goto_page(2)
            elif self.current_values['document_class'] == 'book': self.goto_page(3)
            elif self.current_values['document_class'] == 'letter': self.goto_page(4)
            elif self.current_values['document_class'] == 'beamer': self.goto_page(5)
        elif self.current_page in range(1, 6):
            self.goto_page(6)

    def goto_page_prev(self, button=None, data=None):
        if self.current_page == 6:
            if self.current_values['document_class'] == 'article': self.goto_page(1)
            elif self.current_values['document_class'] == 'report': self.goto_page(2)
            elif self.current_values['document_class'] == 'book': self.goto_page(3)
            elif self.current_values['document_class'] == 'letter': self.goto_page(4)
            elif self.current_values['document_class'] == 'beamer': self.goto_page(5)
        elif self.current_page in range(1, 6):
            self.goto_page(0)

    def goto_page(self, page_number):
        self.current_page = page_number
        self.view.notebook.set_current_page(page_number)
        self.view.headerbar.set_subtitle(self.view.pages[page_number].headerbar_subtitle)
        
        if page_number == 0:
            GLib.idle_add(self.view.document_class_page.list_grab_focus)
        elif page_number == 1:
            GLib.idle_add(self.view.article_settings_page.list_grab_focus)
        elif page_number == 2:
            GLib.idle_add(self.view.report_settings_page.list_grab_focus)
        elif page_number == 3:
            GLib.idle_add(self.view.book_settings_page.list_grab_focus)
        elif page_number == 4:
            GLib.idle_add(self.view.letter_settings_page.list_grab_focus)
        elif page_number == 5:
            GLib.idle_add(self.view.beamer_settings_page.list_grab_focus)
        elif page_number == 6:
            GLib.idle_add(self.view.general_settings_page.title_entry.grab_focus)

        if page_number == 0:
            self.view.back_button.hide()
            self.view.create_button.hide()
            self.view.next_button.show_all()
        elif page_number < 6:
            self.view.create_button.hide()
            self.view.back_button.show_all()
            self.view.next_button.show_all()
        else:
            self.view.next_button.hide()
            self.view.back_button.show_all()
            self.view.create_button.show_all()

    def observe_document_class_page(self):
        def row_selected(box, row, user_data=None):
            child_name = row.get_child().get_text().lower()
            self.current_values['document_class'] = child_name
            self.view.document_class_page.preview_container.set_visible_child_name(child_name)

        self.view.document_class_page.list.connect('row-selected', row_selected)

    def observe_article_settings_page(self):
        def row_selected(box, row, user_data=None):
            child_name = row.get_child().get_text()
            self.current_values['article']['page_format'] = child_name

        def scale_change_value(scale, scroll, value, user_data=None):
            self.current_values['article']['font_size'] = int(value)

        def option_toggled(button, option_name):
            self.current_values['article']['option_' + option_name] = button.get_active()

        self.view.article_settings_page.page_format_list.connect('row-selected', row_selected)
        self.view.article_settings_page.font_size_entry.connect('change-value', scale_change_value)
        self.view.article_settings_page.option_twocolumn.connect('toggled', option_toggled, 'twocolumn')

    def observe_report_settings_page(self):
        def row_selected(box, row, user_data=None):
            child_name = row.get_child().get_text()
            self.current_values['report']['page_format'] = child_name

        def scale_change_value(scale, scroll, value, user_data=None):
            self.current_values['report']['font_size'] = int(value)

        def option_toggled(button, option_name):
            self.current_values['report']['option_' + option_name] = button.get_active()

        self.view.report_settings_page.page_format_list.connect('row-selected', row_selected)
        self.view.report_settings_page.font_size_entry.connect('change-value', scale_change_value)
        self.view.report_settings_page.option_twocolumn.connect('toggled', option_toggled, 'twocolumn')

    def observe_book_settings_page(self):
        def row_selected(box, row, user_data=None):
            child_name = row.get_child().get_text()
            self.current_values['book']['page_format'] = child_name

        def scale_change_value(scale, scroll, value, user_data=None):
            self.current_values['book']['font_size'] = int(value)

        def option_toggled(button, option_name):
            self.current_values['book']['option_' + option_name] = button.get_active()

        self.view.book_settings_page.page_format_list.connect('row-selected', row_selected)
        self.view.book_settings_page.font_size_entry.connect('change-value', scale_change_value)
        self.view.book_settings_page.option_twocolumn.connect('toggled', option_toggled, 'twocolumn')

    def observe_letter_settings_page(self):
        def row_selected(box, row, user_data=None):
            child_name = row.get_child().get_text()
            self.current_values['letter']['page_format'] = child_name

        def scale_change_value(scale, scroll, value, user_data=None):
            self.current_values['letter']['font_size'] = int(value)

        self.view.letter_settings_page.page_format_list.connect('row-selected', row_selected)
        self.view.letter_settings_page.font_size_entry.connect('change-value', scale_change_value)

    def observe_beamer_settings_page(self):
        def row_selected(box, row, user_data=None):
            child_name = row.get_child().get_text()
            self.current_values['beamer']['theme'] = child_name
            image_box = self.view.beamer_settings_page.preview_image_boxes[child_name][0]
            if image_box.get_center_widget() == None:
                image_box.set_center_widget(page.preview_images[child_name][0])
                image_box.show_all()
            self.view.beamer_settings_page.preview_stack.set_transition_type(Gtk.StackTransitionType.NONE)
            self.view.beamer_settings_page.preview_stack.set_visible_child_name(child_name + '_0')

            button = self.view.beamer_settings_page.preview_buttons[child_name][0]
            button.set_image(page.preview_button_images[child_name][0])
            button = self.view.beamer_settings_page.preview_buttons[child_name][1]
            button.set_image(page.preview_button_images[child_name][1])
            self.view.beamer_settings_page.preview_button_stack.set_visible_child_name(child_name)

        def option_toggled(button, option_name):
            self.current_values['beamer']['option_' + option_name] = button.get_active()

        def preview_button_clicked(button, theme_name, number):
            stack = self.view.beamer_settings_page.preview_stack
            if number == 0:
                stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
            elif number == 1:
                stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
            stack.set_visible_child_name(theme_name + '_' + str(number))

        self.view.beamer_settings_page.themes_list.connect('row-selected', row_selected)
        self.view.beamer_settings_page.option_show_navigation.connect('toggled', option_toggled, 'show_navigation')
        self.view.beamer_settings_page.option_top_align.connect('toggled', option_toggled, 'top_align')
        page = self.view.beamer_settings_page
        for name in self.view.beamer_settings_page.theme_names:
            for i in range(0, 2):
                button = self.view.beamer_settings_page.preview_buttons[name][i]
                button.set_can_focus(False)
                button.connect('clicked', preview_button_clicked, name, i)

    def observe_general_settings_page(self):
        def text_deleted(buffer, position, n_chars, field_name):
            self.current_values[field_name] = buffer.get_text()

        def text_inserted(buffer, position, chars, n_chars, field_name):
            self.current_values[field_name] = buffer.get_text()

        def option_toggled(button, package_name):
            self.current_values['packages'][package_name] = button.get_active()

        def package_hover_start(button, event, package_name):
            markup = self.view.general_settings_page.packages_tooltip_data[package_name]
            self.view.general_settings_page.packages_tooltip.set_markup(markup)

        def package_hover_end(button, event, package_name):
            self.view.general_settings_page.packages_tooltip.set_markup(' ')

        page = self.view.general_settings_page
        page.title_entry.get_buffer().connect('deleted-text', text_deleted, 'title')
        page.title_entry.get_buffer().connect('inserted-text', text_inserted, 'title')
        page.author_entry.get_buffer().connect('deleted-text', text_deleted, 'author')
        page.author_entry.get_buffer().connect('inserted-text', text_inserted, 'author')
        page.date_entry.get_buffer().connect('deleted-text', text_deleted, 'date')
        page.date_entry.get_buffer().connect('inserted-text', text_inserted, 'date')
        for name, checkbox in self.view.general_settings_page.option_packages.items():
            checkbox.connect('toggled', option_toggled, name)
            checkbox.connect('enter-notify-event', package_hover_start, name)
            checkbox.connect('leave-notify-event', package_hover_end, name)

    def on_keypress(self, widget, event, data=None):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.keyval == Gdk.keyval_from_name('Return'):
            if event.state & modifiers == 0:
                if self.current_page in range(0, 6):
                    self.view.next_button.clicked()
                    return True
                elif self.current_page == 6:
                    self.view.create_button.clicked()
                    return True
        return False

    def insert_template(self, data=None):
        buff = self.document.get_buffer()
        if buff != False:
            buff.begin_user_action()

            document_class = self.current_values['document_class']

            bounds = buff.get_bounds()
            text = buff.get_text(bounds[0], bounds[1], True)
            line_count_before_insert = buff.get_line_count()

            insert_start, insert_end = eval('self.get_insert_text_' + document_class + '()')
            insert_start_orig_len = len(insert_start)

            bounds = buff.get_bounds()
            buff.insert(bounds[0], insert_start)
            bounds = buff.get_bounds()
            buff.insert(bounds[1], insert_end)

            bounds = buff.get_bounds()
            bounds[0].forward_chars(insert_start_orig_len)
            buff.place_cursor(bounds[0])

            buff.end_user_action()
            buff.begin_user_action()

            if len(text.strip()) > 0:
                offset = buff.get_iter_at_mark(buff.get_insert()).get_line()
                buff.insert(buff.get_iter_at_line(offset), 
'''% NOTE: The content of your document has been commented out
% by the wizard. Just do a CTRL+Z (undo) to put it back in
% or remove the "%" before each line you want to keep.
% You can remove this note as well.
% 
''')
                for line_number in range(offset + 5, line_count_before_insert + offset + 5):
                    buff.insert(buff.get_iter_at_line(line_number), '% ')
                insert_iter = buff.get_iter_at_mark(buff.get_insert())
                insert_iter.backward_chars(215)
                buff.place_cursor(insert_iter)

            buff.end_user_action()
            
    '''
    *** templates
    '''
    
    def get_insert_text_article(self):
        return ('''\\documentclass[''' + self.page_formats[self.current_values['article']['page_format']] + ''',''' + str(self.current_values['article']['font_size']) + '''pt''' + (',twocolumn' if self.current_values['article']['option_twocolumn'] else '') + ''']{article}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage{lmodern}
''' + self.get_insert_packages() + '''
\\title{''' + self.current_values['title'] + '''}
\\author{''' + self.current_values['author'] + '''}
\\date{''' + self.current_values['date'] + '''}

\\begin{document}

\\maketitle
\\tableofcontents

\\begin{abstract}
\\end{abstract}

\\section{}

''', '''

\\end{document}''')

    def get_insert_text_report(self):
        return ('''\\documentclass[''' + self.page_formats[self.current_values['report']['page_format']] + ''',''' + str(self.current_values['report']['font_size']) + '''pt''' + (',twocolumn' if self.current_values['report']['option_twocolumn'] else '') + ''']{report}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage{lmodern}
''' + self.get_insert_packages() + '''
\\title{''' + self.current_values['title'] + '''}
\\author{''' + self.current_values['author'] + '''}
\\date{''' + self.current_values['date'] + '''}

\\begin{document}

\\maketitle
\\tableofcontents

\\begin{abstract}
\\end{abstract}

\\chapter{}

''', '''

\\end{document}''')

    def get_insert_text_book(self):
        return ('''\\documentclass[''' + self.page_formats[self.current_values['book']['page_format']] + ''',''' + str(self.current_values['book']['font_size']) + '''pt''' + (',twocolumn' if self.current_values['book']['option_twocolumn'] else '') + ''']{book}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage{lmodern}
''' + self.get_insert_packages() + '''
\\title{''' + self.current_values['title'] + '''}
\\author{''' + self.current_values['author'] + '''}
\\date{''' + self.current_values['date'] + '''}

\\begin{document}

\\maketitle
\\tableofcontents

\\chapter{}

''', '''

\\end{document}''')

    def get_insert_text_letter(self):
        return ('''\\documentclass[''' + self.page_formats[self.current_values['letter']['page_format']] + ''',''' + str(self.current_values['letter']['font_size']) + '''pt''' + (',twocolumn' if self.current_values['letter']['option_twocolumn'] else '') + ''']{letter}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage{lmodern}
''' + self.get_insert_packages() + '''
\\address{Your name\\\\Your address\\\\Your phone number}
\\date{''' + self.current_values['date'] + '''}
\\signature{''' + self.current_values['author'] + '''}

\\begin{document}

\\begin{letter}{Destination\\\\Address of the destination\\\\Phone number of the destination''' + ('''\\\\~\\\\\\textbf{''' + self.current_values['title'] + '''}''' if len(self.current_values['title']) > 0 else '') + '''}

\\opening{Dear addressee,}

''', '''

\\closing{Yours sincerely,}

%\\cc{Other destination}
%\\ps{PS: PostScriptum}
%\\encl{Enclosures}

\\end{letter}
\\end{document}''')

    def get_insert_text_beamer(self):
        theme = self.current_values['beamer']['theme']
        top_align = '[t]' if self.current_values['beamer']['option_top_align'] else ''
        show_navigation = '''

\\beamertemplatenavigationsymbolsempty''' if not self.current_values['beamer']['option_show_navigation'] else ''

        return ('''\\documentclass''' + top_align + '''{beamer}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage{lmodern}
''' + self.get_insert_packages() + '''\\usetheme{''' + theme + '''}''' + show_navigation + '''

\\title{''' + self.current_values['title'] + '''}
\\author{''' + self.current_values['author'] + '''}
\\date{''' + self.current_values['date'] + '''}

\\begin{document}

\\begin{frame}
  \\titlepage
\\end{frame}

''', '''

\\end{document}''')

    def get_insert_packages(self):
        text = ''
        if self.current_values['packages']['ams']:
            text += '''\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{amsthm}
'''
        for package_name, do_insert in self.current_values['packages'].items():
            if package_name != 'ams' and do_insert:
                text += '\\usepackage{' + package_name + '}\n'
        return text


