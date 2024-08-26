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

import os.path

import setzer.helpers.path as path_helpers
from setzer.app.service_locator import ServiceLocator


class LaTeXLogParser():

    def __init__(self):
        self.doc_regex = ServiceLocator.get_regex_object(r'(\(([^\(\)]*\.(?:tex|gls)))')
        self.item_regex = ServiceLocator.get_regex_object(r'((?<!.) *' + 
    r'(?:Overfull \\hbox|Underfull \\hbox|' + 
    r'No file .*\.|File .* does not exist\.|' +
    r'(?:LaTeX|pdfTeX|LuaTeX|Package|Class) .*Warning.*:|LaTeX Font Warning:|' +
    r'!(?: )(?:LaTeX|pdfTeX|LuaTeX|Package|Class) error|' +
    r'! ).*\n)')
        self.badbox_line_number_regex = ServiceLocator.get_regex_object(r'lines ([0-9]+)--([0-9]+)')
        self.other_line_number_regex = ServiceLocator.get_regex_object(r'(l\.| input line \n| input line )([0-9]+)( |\.)')

    def parse_build_log(self, tex_filename):
        log_filename = os.path.dirname(tex_filename) + '/' + os.path.basename(tex_filename).rsplit('.tex', 1)[0] + '.log'
        try: file = open(log_filename, 'rb')
        except FileNotFoundError as e: raise e
        else:
            text = file.read().decode('utf-8', errors='ignore')

        doc_texts = self.split_log_text_by_file(text, tex_filename)

        log_items = dict()
        for filename, text in doc_texts.items():
            filename = ''.join(filename.splitlines())
            log_items[filename] = self.parse_log_text(filename, text)

        return log_items

    def get_additional_jobs(self, log_items, query):
        jobs = set()
        rerun_latex_reasons = set()
        for filename, items in log_items.items():
            for item in items['error'] + items['warning']:

                if item[2].startswith('No file ') and item[2].find(query.tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and item[2].find('.bbl.') >= 0:
                    if not query.tex_filename.rsplit('/', 1)[1][:-4] in query.bibtex_data['ran_on_files']:
                        jobs |= {'build_bibtex'}

                elif item[2].startswith('No file ') and item[2].find(query.tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and item[2].find('.ind.') >= 0:
                    if not query.tex_filename.rsplit('/', 1)[1][:-4] in query.makeindex_data['ran_on_files']:
                        jobs |= {'build_makeindex'}

                elif item[2] == 'Please (re)run Biber on the file:':
                    line = item[3]
                    if line.find(query.tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0:
                        if not query.tex_filename.rsplit('/', 1)[1][:-4] in query.biber_data['ran_on_files']:
                            jobs |= {'build_biber'}

                elif item[2] == 'File `' + query.tex_filename.rsplit('/', 1)[1][:-4] + '.out\' has changed.':
                    jobs |= {'build_latex'}
                    rerun_latex_reasons |= {1}

                elif item[2] == 'Please rerun LaTeX.':
                    jobs |= {'build_latex'}
                    rerun_latex_reasons |= {2}

                elif item[2] == 'Label(s) may have changed. Rerun to get cross-references right.':
                    jobs |= {'build_latex'}
                    rerun_latex_reasons |= {3}

                elif item[2] == 'There were undefined references.':
                    jobs |= {'build_latex'}
                    rerun_latex_reasons |= {3}

                elif item[2] == 'Citation(s) may have changed.':
                    jobs |= {'build_latex'}
                    rerun_latex_reasons |= {4}

                elif item[2].startswith('No file ') and item[2].find(query.tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and (item[2].find('.toc.') >= 0 or item[2].find('.aux.') >= 0):
                    jobs |= {'build_latex'}
                    rerun_latex_reasons |= {5}

                elif item[2] == 'Rerun to get transparencies right.':
                    jobs |= {'build_latex'}
                    rerun_latex_reasons |= {6}

                elif item[2].startswith('No file ') and item[2].find(query.tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and (item[2].find('.gls.') >= 0 or item[2].find('.acr.') >= 0):
                    jobs |= {'build_glossaries'}

                elif item[2].startswith('No file ') and item[2].find(query.tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and (item[2].find('.aux.') >= 0):
                    jobs |= {'build_latex'}
                    rerun_latex_reasons |= {7}

        if 'build_biber' in jobs:
            return {'build_biber'}
        if 'build_bibtex' in jobs:
            return {'build_bibtex'}
        if 'build_makeindex' in jobs:
            return {'build_makeindex'}
        if 'build_glossaries' in jobs:
            return {'build_glossaries'}
        if 'build_latex' in jobs:
            if len(rerun_latex_reasons - query.build_data['rerun_latex_reasons']) > 0:
                query.build_data['rerun_latex_reasons'] = rerun_latex_reasons
                return {'build_latex'}
            else:
                jobs -= {'build_latex'}
        return jobs

    def parse_log_text(self, filename, text):
        log_messages = {'error': list(), 'warning': list(), 'badbox': list()}
        matches = self.item_regex.split(text)
        buffer = ''
        for match in reversed(matches):
            if not self.item_regex.fullmatch(match):
                buffer += match
            else:
                match += buffer
                buffer = ''
                matchiter = iter(match.splitlines())
                line = next(matchiter)

                if line.startswith('No file '):
                    text = line.strip()
                    line_number = -1
                    log_messages['warning'].append((None, line_number, text))

                elif line.startswith('Package biblatex Warning: Please (re)run Biber on the file:'):
                    text = line[26:].strip()
                    line = next(matchiter)
                    log_messages['warning'].append((None, -1, text, line))

                elif line.startswith('Package biblatex Warning: Please rerun LaTeX.'):
                    text = line[26:].strip()
                    log_messages['warning'].append((None, -1, text))

                elif line.startswith('LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.'):
                    text = line[15:].strip()
                    log_messages['warning'].append((None, -1, text))

                elif line.startswith('Package natbib Warning: Citation(s) may have changed.'):
                    text = line[24:].strip()
                    log_messages['warning'].append((None, -1, text))

                elif line.startswith('Overfull \\hbox'):
                    line_number_match = self.badbox_line_number_regex.search(line)
                    if line_number_match != None:
                        line_number = int(line_number_match.group(1))
                        text = line.strip()
                        log_messages['badbox'].append((None, line_number, text))

                elif line.startswith('Underfull \\hbox'):
                    line_number_match = self.badbox_line_number_regex.search(line)
                    if line_number_match != None:
                        line_number = int(line_number_match.group(1))
                        text = line.strip()
                        log_messages['badbox'].append((None, line_number, text))

                elif line.startswith('LaTeX Warning: Reference '):
                    text = line[15:].strip()
                    line_number = self.bl_get_line_number(line, matchiter)
                    log_messages['warning'].append(('Undefined Reference', line_number, text))

                elif line.startswith('Package '):
                    text = line.split(':')[1].strip()
                    line_number = self.bl_get_line_number(line, matchiter)
                    log_messages['warning'].append((None, line_number, text))

                elif line.startswith('LaTeX Warning: '):
                    text = line[15:].strip()
                    line_number = self.bl_get_line_number(line, matchiter)
                    log_messages['warning'].append((None, line_number, text))

                elif line.startswith('! Undefined control sequence'):
                    text = line.strip()
                    line_number = self.bl_get_line_number(line, matchiter)
                    log_messages['error'].append(('Undefined control sequence', line_number, text))

                elif line.startswith('! LaTeX Error') or line.startswith('!pdfTeX error'):
                    text = line[15:].strip()
                    line_number = self.bl_get_line_number(line, matchiter)
                    log_messages['error'].append((None, line_number, text))

                elif line.startswith('! Package'):
                    text = self.get_text(line[2:], matchiter, True)
                    line_number = self.bl_get_line_number(line, matchiter)
                    log_messages['error'].append(('Undefined control sequence', line_number, text))

                elif line.startswith('File') and line.endswith(' does not exist.\n'):
                    text = line.strip()
                    line_number = -1
                    log_messages['error'].append((None, line_number, text))

                elif line.startswith('! I can\'t find file.'):
                    text = line.strip()
                    line_number = -1
                    log_messages['error'].append((None, line_number, text))

                elif line.startswith('! File'):
                    text = self.get_text(line[2:])
                    line_number = self.bl_get_line_number(line, matchiter)
                    log_messages['error'].append((None, line_number, text))

                elif line.startswith('! ') and not line.startswith('!  ==> Fatal'):
                    text = line[2:].strip()
                    line_number = self.bl_get_line_number(line, matchiter)
                    log_messages['error'].append((None, line_number, text))
        return log_messages

    def get_text(self, line, matchiter=None, can_be_multiline=False):
        if can_be_multiline:
            text = line.strip()
            if not '.' in text and len(text) > 60:
                try:
                    text += next(matchiter).strip()
                except StopIteration:
                    pass
            return text
        else:
            return line.strip()

    def split_log_text_by_file(self, log_text, tex_filename):
        doc_texts = dict()

        matches = self.doc_regex.split(log_text)
        buffer = ''
        for match in reversed(matches):
            if not self.doc_regex.fullmatch(match):
                buffer += match
            else:
                match = match.strip() + buffer
                buffer = ''
                filename = self.doc_regex.match(match).group(2).strip()
                if not filename.startswith('/'):
                    filename = path_helpers.get_abspath(filename, os.path.dirname(tex_filename))
                else:
                    filename = os.path.normpath(filename)
                if not filename == tex_filename:
                    open_brackets = 0
                    char_count = 0
                    for char in match:
                        if char == ')':
                            open_brackets -= 1
                        if char == '(':
                            open_brackets += 1
                        char_count += 1
                        if open_brackets == 0:
                            break
                    match = match[:char_count]
                    doc_texts[filename] = match
                    log_text = log_text.replace(match, '')
                buffer = ''
        doc_texts[tex_filename] = log_text
        return doc_texts

    def bl_get_line_number(self, line, matchiter):
        for i in range(10):
            line_number_match = self.other_line_number_regex.search(line)
            if line_number_match != None:
                return int(line_number_match.group(2))
            else:
                try:
                    line += next(matchiter)
                except StopIteration:
                    return -1
        return -1


