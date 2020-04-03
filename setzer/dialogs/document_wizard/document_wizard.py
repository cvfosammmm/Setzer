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
from gi.repository import Gdk

from setzer.dialogs.dialog import Dialog
import setzer.dialogs.document_wizard.document_wizard_viewgtk as view
from setzer.dialogs.document_wizard.pages.page_document_class import DocumentClassPage
from setzer.dialogs.document_wizard.pages.page_article_settings import ArticleSettingsPage
from setzer.dialogs.document_wizard.pages.page_report_settings import ReportSettingsPage
from setzer.dialogs.document_wizard.pages.page_book_settings import BookSettingsPage
from setzer.dialogs.document_wizard.pages.page_letter_settings import LetterSettingsPage
from setzer.dialogs.document_wizard.pages.page_beamer_settings import BeamerSettingsPage
from setzer.dialogs.document_wizard.pages.page_general_settings import GeneralSettingsPage

import pickle
import os


class DocumentWizard(Dialog):
    ''' Create document templates for users to build on. '''

    def __init__(self, main_window, workspace, settings, resources_path):
        self.main_window = main_window
        self.workspace = workspace
        self.settings = settings
        self.current_values = dict()
        self.page_formats = {'US Letter': 'letterpaper', 'US Legal': 'legalpaper', 'A4': 'a4paper', 'A5': 'a5paper', 'B5': 'b5paper'}

        self.view = view.DocumentWizardView(self.main_window)

        self.pages = list()
        self.pages.append(DocumentClassPage(self.current_values, resources_path))
        self.pages.append(ArticleSettingsPage(self.current_values))
        self.pages.append(ReportSettingsPage(self.current_values))
        self.pages.append(BookSettingsPage(self.current_values))
        self.pages.append(LetterSettingsPage(self.current_values))
        self.pages.append(BeamerSettingsPage(self.current_values, resources_path))
        self.pages.append(GeneralSettingsPage(self.current_values))
        for page in self.pages: self.view.notebook.append_page(page.view)

        self.is_not_setup = True

    def run(self, document):
        self.document = document

        if self.is_not_setup:
            self.init_current_values()
            self.setup()
            self.is_not_setup = False

        self.presets = None
        self.current_page = 0
        self.load_presets()
        self.goto_page(0)

        response = self.view.run()

        if response == Gtk.ResponseType.APPLY:
            self.save_presets()
            self.insert_template()

        self.view.dialog.hide()

    def init_current_values(self):
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
        self.current_values['article']['option_default_margins'] = True
        self.current_values['article']['margin_left'] = 3.5
        self.current_values['article']['margin_right'] = 3.5
        self.current_values['article']['margin_top'] = 3.5
        self.current_values['article']['margin_bottom'] = 3.5
        self.current_values['article']['is_landscape'] = False
        self.current_values['report'] = dict()
        self.current_values['report']['page_format'] = 'US Letter'
        self.current_values['report']['font_size'] = 11
        self.current_values['report']['option_twocolumn'] = False
        self.current_values['report']['option_default_margins'] = True
        self.current_values['report']['margin_left'] = 3.5
        self.current_values['report']['margin_right'] = 3.5
        self.current_values['report']['margin_top'] = 3.5
        self.current_values['report']['margin_bottom'] = 3.5
        self.current_values['report']['is_landscape'] = False
        self.current_values['book'] = dict()
        self.current_values['book']['page_format'] = 'US Letter'
        self.current_values['book']['font_size'] = 11
        self.current_values['book']['option_twocolumn'] = False
        self.current_values['book']['option_default_margins'] = True
        self.current_values['book']['margin_left'] = 3.5
        self.current_values['book']['margin_right'] = 3.5
        self.current_values['book']['margin_top'] = 3.5
        self.current_values['book']['margin_bottom'] = 3.5
        self.current_values['book']['is_landscape'] = False
        self.current_values['letter'] = dict()
        self.current_values['letter']['page_format'] = 'US Letter'
        self.current_values['letter']['font_size'] = 11
        self.current_values['letter']['option_default_margins'] = True
        self.current_values['letter']['margin_left'] = 3.5
        self.current_values['letter']['margin_right'] = 3.5
        self.current_values['letter']['margin_top'] = 3.5
        self.current_values['letter']['margin_bottom'] = 3.5
        self.current_values['beamer'] = dict()
        self.current_values['beamer']['theme'] = 'Default'
        self.current_values['beamer']['option_show_navigation'] = True
        self.current_values['beamer']['option_top_align'] = True
    
    def setup(self):
        self.view.dialog.connect('key-press-event', self.on_keypress)
        for page in self.pages: page.observe_view()
        self.view.next_button.connect('clicked', self.goto_page_next)
        self.view.back_button.connect('clicked', self.goto_page_prev)

    def load_presets(self):
        if self.presets == None:
            presets = self.settings.get_value('app_document_wizard', 'presets')
            if presets != None: self.presets = pickle.loads(presets)

        for page in self.pages:
            page.load_presets(self.presets)

    def save_presets(self):
        self.settings.set_value('app_document_wizard', 'presets', pickle.dumps(self.current_values))

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
        self.view.headerbar.set_subtitle(self.pages[page_number].view.headerbar_subtitle)
        
        self.pages[page_number].on_activation()

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

            # replace tabs with spaces, if set in preferences
            if self.settings.get_value('preferences', 'spaces_instead_of_tabs'):
                number_of_spaces = self.settings.get_value('preferences', 'tab_width')
                insert_start = insert_start.replace('\t', ' ' * number_of_spaces)
                insert_end = insert_end.replace('\t', ' ' * number_of_spaces)

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
        return ('''\\documentclass[''' + self.page_formats[self.current_values['article']['page_format']] + ''',''' + str(self.current_values['article']['font_size']) + '''pt''' + (',twocolumn' if self.current_values['article']['option_twocolumn'] else '') + (',landscape' if self.current_values['article']['is_landscape'] else '') + ''']{article}
''' +
('''\\usepackage[top=''' + str(self.current_values['article']['margin_top']) + '''cm, bottom=''' + str(self.current_values['article']['margin_bottom']) + '''cm, left=''' + str(self.current_values['article']['margin_left']) + '''cm, right=''' + str(self.current_values['article']['margin_right']) + '''cm]{geometry}''' if not self.current_values['article']['option_default_margins'] else '')
+ '''\\usepackage[T1]{fontenc}
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
        return ('''\\documentclass[''' + self.page_formats[self.current_values['report']['page_format']] + ''',''' + str(self.current_values['report']['font_size']) + '''pt''' + (',twocolumn' if self.current_values['report']['option_twocolumn'] else '') + (',landscape' if self.current_values['report']['is_landscape'] else '') + ''']{report}
''' +
('''\\usepackage[top=''' + str(self.current_values['report']['margin_top']) + '''cm, bottom=''' + str(self.current_values['report']['margin_bottom']) + '''cm, left=''' + str(self.current_values['report']['margin_left']) + '''cm, right=''' + str(self.current_values['report']['margin_right']) + '''cm]{geometry}''' if not self.current_values['report']['option_default_margins'] else '')
+ '''\\usepackage[T1]{fontenc}
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
        return ('''\\documentclass[''' + self.page_formats[self.current_values['book']['page_format']] + ''',''' + str(self.current_values['book']['font_size']) + '''pt''' + (',twocolumn' if self.current_values['book']['option_twocolumn'] else '') + (',landscape' if self.current_values['book']['is_landscape'] else '') + ''']{book}
''' +
('''\\usepackage[top=''' + str(self.current_values['book']['margin_top']) + '''cm, bottom=''' + str(self.current_values['book']['margin_bottom']) + '''cm, left=''' + str(self.current_values['book']['margin_left']) + '''cm, right=''' + str(self.current_values['book']['margin_right']) + '''cm]{geometry}''' if not self.current_values['book']['option_default_margins'] else '')
+ '''\\usepackage[T1]{fontenc}
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
        return ('''\\documentclass[''' + self.page_formats[self.current_values['letter']['page_format']] + ''',''' + str(self.current_values['letter']['font_size']) + '''pt]{letter}
''' +
('''\\usepackage[top=''' + str(self.current_values['letter']['margin_top']) + '''cm, bottom=''' + str(self.current_values['letter']['margin_bottom']) + '''cm, left=''' + str(self.current_values['letter']['margin_left']) + '''cm, right=''' + str(self.current_values['letter']['margin_right']) + '''cm]{geometry}''' if not self.current_values['letter']['option_default_margins'] else '')
+ '''\\usepackage[T1]{fontenc}
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


