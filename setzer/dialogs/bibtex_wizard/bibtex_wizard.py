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
import setzer.dialogs.bibtex_wizard.bibtex_wizard_viewgtk as view
from setzer.dialogs.bibtex_wizard.pages.page_create_new_entry import CreateNewEntryPage
from setzer.dialogs.bibtex_wizard.pages.page_fields_entry import FieldsEntryPage
from setzer.app.service_locator import ServiceLocator

import pickle
import os


class BibTeXWizard(Dialog):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace
        self.settings = ServiceLocator.get_settings()
        self.document_types = dict()
        self.document_types['article'] = {'title': _('Article in Journal'), 'description': _('An article in a journal, magazine, newspaper, or other periodical which forms a self-contained unit with its own title. The title of the periodical is given in the <tt>journaltitle</tt> field. If the issue has its own title in addition to the main title of the periodical, it goes in the <tt>issuetitle</tt> field. Note that <tt>editor</tt> and related fields refer to the journal while <tt>translator</tt> and related fields refer to the article.'), 'fields_required': ['author', 'title', 'journaltitle', 'date'], 'fields_optional': ['translator', 'annotator', 'commentator', 'subtitle', 'titleaddon', 'editor', 'editora', 'editorb', 'editorc', 'journalsubtitle', 'issuetitle', 'issuesubtitle', 'language', 'origlanguage', 'series', 'volume', 'number', 'eid', 'issue', 'month', 'pages', 'version', 'note', 'issn', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['book'] = {'title': _('Book'), 'description': _('A single-volume book with one or more authors where the authors share credit for the work as a whole. This entry type also covers the function of the @inbook type of traditional BibTeX.'), 'fields_required': ['author', 'title', 'date'], 'fields_optional': ['editor', 'editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['mvbook'] = {'title': _('Multi-volume Book'), 'description': _('A multi-volume @book. For backwards compatibility, multi-volume books are also supported by the entry type @book. However, it is advisable to make use of the dedicated entry type @mvbook.'), 'fields_required': ['author', 'title', 'date'], 'fields_optional': ['editor', 'editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'language', 'origlanguage', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['inbook'] = {'title': _('Part of a Book With Its Own Title'), 'description': _('A part of a book which forms a self-contained unit with its own title. Note that the profile of this entry type is different from standard BibTeX.'), 'fields_required': ['author', 'title', 'booktitle', 'date'], 'fields_optional': ['bookauthor', 'editor', 'editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'booksubtitle', 'booktitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['bookinbook'] = {'title': _('Book in Book'), 'description': _('This type is similar to @inbook but intended for works originally published as a stand-alone book. A typical example are books reprinted in the collected works of an author.'), 'fields_required': ['author', 'title', 'booktitle', 'date'], 'fields_optional': ['bookauthor', 'editor', 'editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'booksubtitle', 'booktitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['suppbook'] = {'title': _('Supplemental Material in a Book'), 'description': _('Supplemental material in a @book. This type is closely related to the @inbook entry type. While @inbook is primarily intended for a part of a book with its own title (e. g., a single essay in a collection of essays by the same author), this type is provided for elements such as prefaces, introductions, forewords, afterwords, etc. which often have a generic title only. Style guides may require such items to be formatted differently from other @inbook items. The standard styles will treat this entry type as an alias for @inbook.'), 'fields_required': ['author', 'title', 'booktitle', 'date'], 'fields_optional': ['bookauthor', 'editor', 'editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'booksubtitle', 'booktitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['booklet'] = {'title': _('Booklet'), 'description': _('A book-like work without a formal publisher or sponsoring institution. Use the field <tt>howpublished</tt> to supply publishing information in free format, if applicable. The field <tt>type</tt> may be useful as well.'), 'fields_required': ['author/editor', 'title', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'howpublished', 'type', 'note', 'location', 'chapter', 'pages', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['collection'] = {'title': _('Single-volume Collection'), 'description': _('A single-volume collection with multiple, self-contained contributions by distinct authors which have their own title. The work as a whole has no overall author but it will usually have an editor.'), 'fields_required': ['editor', 'title', 'date'], 'fields_optional': ['editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['mvcollection'] = {'title': _('Multi-volume Collection'), 'description': _('A multi-volume @collection. For backwards compatibility, multi-volume collections are also supported by the entry type @collection. However, it is advisable to make use of the dedicated entry type @mvcollection.'), 'fields_required': ['editor', 'title', 'date'], 'fields_optional': ['editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'language', 'origlanguage', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['incollection'] = {'title': _('Article in a Collection'), 'description': _('A contribution to a collection which forms a self-contained unit with a distinct author and title. The <tt>author</tt> refers to the <tt>title</tt>, the <tt>editor</tt> to the <tt>booktitle</tt>, i. e., the title of the collection.'), 'fields_required': ['author', 'editor', 'title', 'booktitle', 'date'], 'fields_optional': ['editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'booksubtitle', 'booktitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['suppcollection'] = {'title': _('Supplemental Material in a Collection'), 'description': _('Supplemental material in a @collection. This type is similar to @suppbook but related to the @collection entry type. The standard styles will treat this entry type as an alias for @incollection.'), 'fields_required': ['author', 'title', 'booktitle', 'date'], 'fields_optional': ['bookauthor', 'editor', 'editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'booksubtitle', 'booktitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['dataset'] = {'title': _('Data Set'), 'description': _('A data set or a similar collection of (mostly) raw data.'), 'fields_required': ['author/editor', 'title', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'edition', 'type', 'series', 'number', 'version', 'note', 'organization', 'publisher', 'location', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['manual'] = {'title': _('Technical Manual'), 'description': _('Technical or other documentation, not necessarily in printed form. The <tt>author</tt> or <tt>editor</tt> is omissible under certain terms.'), 'fields_required': ['author/editor', 'title', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'edition', 'type', 'series', 'number', 'version', 'note', 'organization', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['misc'] = {'title': _('Miscellaneous'), 'description': _('A fallback type for entries which do not fit into any other category. Use the field <tt>howpublished</tt> to supply publishing information in free format, if applicable. The field type may be useful as well. <tt>author</tt>, <tt>editor</tt>, and <tt>year</tt> are omissible under certain terms.'), 'fields_required': ['author/editor', 'title', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'howpublished', 'type', 'version', 'note', 'organization', 'location', 'date', 'month', 'year', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['online'] = {'title': _('Online Resource'), 'description': _('An online resource. <tt>author</tt>, <tt>editor</tt>, and <tt>year</tt> are omissible under certain terms. This entry type is intended for sources such as web sites which are intrinsically online resources. Note that all entry types support the <tt>url</tt> field. For example, when adding an article from an online journal, it may be preferable to use the @article type and its <tt>url</tt> field.'), 'fields_required': ['author/editor', 'title', 'date', 'url'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'version', 'note', 'organization', 'date', 'month', 'year', 'addendum', 'pubstate', 'urldate']}
        self.document_types['patent'] = {'title': _('Patent'), 'description': _('A patent or patent request. The number or record token is given in the <tt>number</tt> field. Use the <tt>type</tt> field to specify the type and the <tt>location</tt> field to indicate the scope of the patent, if different from the scope implied by the <tt>type</tt>. Note that the <tt>location</tt> field is treated as a key list with this entry type.'), 'fields_required': ['author', 'title', 'number', 'date'], 'fields_optional': ['holder', 'subtitle', 'titleaddon', 'type', 'version', 'location', 'note', 'date', 'month', 'year', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['periodical'] = {'title': _('Complete Issue of a Periodical'), 'description': _('An complete issue of a periodical, such as a special issue of a journal. The title of the periodical is given in the <tt>title</tt> field. If the issue has its own title in addition to the main title of the periodical, it goes in the <tt>issuetitle</tt> field. The <tt>editor</tt> is omissible under certain terms.'), 'fields_required': ['editor', 'title', 'date'], 'fields_optional': ['editora', 'editorb', 'editorc', 'subtitle', 'issuetitle', 'issuesubtitle', 'language', 'series', 'volume', 'number', 'issue', 'date', 'month', 'year', 'note', 'issn', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['suppperiodical'] = {'title': _('Supplemental Material in a Periodical'), 'description': _('Supplemental material in a @periodical. This type is similar to @suppbook but related to the @periodical entry type. The role of this entry type may be more obvious if you bear in mind that the @article type could also be called @inperiodical. This type may be useful when referring to items such as regular columns, obituaries, letters to the editor, etc. which only have a generic title. Style guides may require such items to be formatted differently from articles in the strict sense of the word. The standard styles will treat this entry type as an alias for @article.'), 'fields_required': ['author', 'title', 'booktitle', 'date'], 'fields_optional': ['bookauthor', 'editor', 'editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'booksubtitle', 'booktitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['proceedings'] = {'title': _('Conference Proceedings'), 'description': _('A single-volume conference proceedings. This type is very similar to @collection. It supports an optional <tt>organization</tt> field which holds the sponsoring institution. The <tt>editor</tt> is omissible under certain terms.'), 'fields_required': ['editor', 'title', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'eventtitle', 'eventdate', 'venue', 'language', 'volume', 'part', 'volumes', 'series', 'number', 'note', 'organization', 'publisher', 'location', 'month', 'isbn', 'chapter', 'pages', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['mvproceedings'] = {'title': _('Multi-volume Proceedings Entry'), 'description': _('A multi-volume @proceedings entry. For backwards compatibility, multi-volume proceedings are also supported by the entry type @proceedings. However, it is advisable to make use of the dedicated entry type @mvproceedings.'), 'fields_required': ['editor', 'title', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'eventtitle', 'eventdate', 'venue', 'language', 'volumes', 'series', 'number', 'note', 'organization', 'publisher', 'location', 'month', 'isbn', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['inproceedings'] = {'title': _('Article in Conference Proceedings'), 'description': _('An article in a conference proceedings. This type is similar to @incollection. It supports an optional <tt>organization</tt> field.'), 'fields_required': ['author', 'editor', 'title', 'booktitle', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'booksubtitle', 'booktitleaddon', 'eventtitle', 'eventdate', 'venue', 'language', 'volume', 'part', 'volumes', 'series', 'number', 'note', 'organization', 'publisher', 'location', 'month', 'isbn', 'chapter', 'pages', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['reference'] = {'title': _('Reference'), 'description': _('A single-volume work of reference such as an encyclopedia or a dictionary. This is a more specific variant of the generic @collection entry type. The standard styles will treat this entry type as an alias for @collection.'), 'fields_required': ['editor', 'title', 'date'], 'fields_optional': ['editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['mvreference'] = {'title': _('Multi-volume Reference Entry'), 'description': _('A multi-volume @reference entry. The standard styles will treat this entry type as an alias for @mvcollection. For backwards compatibility, multi-volume references are also supported by the entry type @reference. However, it is advisable to make use of the dedicated entry type @mvreference.'), 'fields_required': ['editor', 'title', 'date'], 'fields_optional': ['editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'language', 'origlanguage', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['inreference'] = {'title': _('Article in a Reference'), 'description': _('An article in a work of reference. This is a more specific variant of the generic @incollection entry type. The standard styles will treat this entry type as an alias for @incollection.'), 'fields_required': ['author', 'editor', 'title', 'booktitle', 'date'], 'fields_optional': ['editora', 'editorb', 'editorc', 'translator', 'annotator', 'commentator', 'introduction', 'foreword', 'afterword', 'subtitle', 'titleaddon', 'maintitle', 'mainsubtitle', 'maintitleaddon', 'booksubtitle', 'booktitleaddon', 'language', 'origlanguage', 'volume', 'part', 'edition', 'volumes', 'series', 'number', 'note', 'publisher', 'location', 'isbn', 'chapter', 'pages', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['report'] = {'title': _('Report'), 'description': _('A technical report, research report, or white paper published by a university or some other institution. Use the <tt>type</tt> field to specify the type of report. The sponsoring institution goes in the <tt>institution</tt> field.'), 'fields_required': ['author', 'title', 'type', 'institution', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'number', 'version', 'note', 'location', 'month', 'isrn', 'chapter', 'pages', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['software'] = {'title': _('Software'), 'description': _('Computer software. The standard styles will treat this entry type as an alias for @misc.'), 'fields_required': ['author/editor', 'title', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'howpublished', 'type', 'version', 'note', 'organization', 'location', 'date', 'month', 'year', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['thesis'] = {'title': _('Thesis'), 'description': _('A thesis written for an educational institution to satisfy the requirements for a degree. Use the <tt>type</tt> field to specify the type of thesis.'), 'fields_required': ['author', 'title', 'type', 'institution', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'note', 'location', 'month', 'isbn', 'chapter', 'pages', 'pagetotal', 'addendum', 'pubstate', 'doi', 'eprint', 'eprintclass', 'eprinttype', 'url', 'urldate']}
        self.document_types['unpublished'] = {'title': _('Unpublished'), 'description': _('A work with an author and a title which has not been formally published, such as a manuscript or the script of a talk. Use the fields <tt>howpublished</tt> and <tt>note</tt> to supply additional information in free format, if applicable.'), 'fields_required': ['author', 'title', 'date'], 'fields_optional': ['subtitle', 'titleaddon', 'language', 'howpublished', 'note', 'location', 'isbn', 'date', 'month', 'year', 'addendum', 'pubstate', 'url', 'urldate']}

        self.fields = dict()
        self.fields['author'] = {'type': '', 'description': ''}
        self.fields['title'] = {'type': '', 'description': ''}
        self.fields['journaltitle'] = {'type': '', 'description': ''}
        self.fields['date'] = {'type': '', 'description': ''}
        self.fields['editor'] = {'type': '', 'description': ''}
        self.fields['editora'] = {'type': '', 'description': ''}
        self.fields['editorb'] = {'type': '', 'description': ''}
        self.fields['editorc'] = {'type': '', 'description': ''}
        self.fields['translator'] = {'type': '', 'description': ''}
        self.fields['annotator'] = {'type': '', 'description': ''}
        self.fields['commentator'] = {'type': '', 'description': ''}
        self.fields['introduction'] = {'type': '', 'description': ''}
        self.fields['foreword'] = {'type': '', 'description': ''}
        self.fields['afterword'] = {'type': '', 'description': ''}
        self.fields['subtitle'] = {'type': '', 'description': ''}
        self.fields['titleaddon'] = {'type': '', 'description': ''}
        self.fields['maintitle'] = {'type': '', 'description': ''}
        self.fields['mainsubtitle'] = {'type': '', 'description': ''}
        self.fields['maintitleaddon'] = {'type': '', 'description': ''}
        self.fields['journalsubtitle'] = {'type': '', 'description': ''}
        self.fields['issuetitle'] = {'type': '', 'description': ''}
        self.fields['issuesubtitle'] = {'type': '', 'description': ''}
        self.fields['language'] = {'type': '', 'description': ''}
        self.fields['origlanguage'] = {'type': '', 'description': ''}
        self.fields['volume'] = {'type': '', 'description': ''}
        self.fields['part'] = {'type': '', 'description': ''}
        self.fields['edition'] = {'type': '', 'description': ''}
        self.fields['volumes'] = {'type': '', 'description': ''}
        self.fields['series'] = {'type': '', 'description': ''}
        self.fields['number'] = {'type': '', 'description': ''}
        self.fields['note'] = {'type': '', 'description': ''}
        self.fields['eid'] = {'type': '', 'description': ''}
        self.fields['issue'] = {'type': '', 'description': ''}
        self.fields['month'] = {'type': '', 'description': ''}
        self.fields['publisher'] = {'type': '', 'description': ''}
        self.fields['location'] = {'type': '', 'description': ''}
        self.fields['isbn'] = {'type': '', 'description': ''}
        self.fields['chapter'] = {'type': '', 'description': ''}
        self.fields['pages'] = {'type': '', 'description': ''}
        self.fields['version'] = {'type': '', 'description': ''}
        self.fields['issn'] = {'type': '', 'description': ''}
        self.fields['pagetotal'] = {'type': '', 'description': ''}
        self.fields['addendum'] = {'type': '', 'description': ''}
        self.fields['pubstate'] = {'type': '', 'description': ''}
        self.fields['doi'] = {'type': '', 'description': ''}
        self.fields['eprint'] = {'type': '', 'description': ''}
        self.fields['eprintclass'] = {'type': '', 'description': ''}
        self.fields['eprinttype'] = {'type': '', 'description': ''}
        self.fields['url'] = {'type': '', 'description': ''}
        self.fields['urldate'] = {'type': '', 'description': ''}
        self.fields['booktitle'] = {'type': '', 'description': ''}
        self.fields['bookauthor'] = {'type': '', 'description': ''}
        self.fields['booksubtitle'] = {'type': '', 'description': ''}
        self.fields['booktitleaddon'] = {'type': '', 'description': ''}
        self.fields['author/editor'] = {'type': '', 'description': ''}
        self.fields['howpublished'] = {'type': '', 'description': ''}
        self.fields['type'] = {'type': '', 'description': ''}
        self.fields['organization'] = {'type': '', 'description': ''}
        self.fields['year'] = {'type': '', 'description': ''}
        self.fields['holder'] = {'type': '', 'description': ''}
        self.fields['eventtitle'] = {'type': '', 'description': ''}
        self.fields['eventdate'] = {'type': '', 'description': ''}
        self.fields['venue'] = {'type': '', 'description': ''}
        self.fields['institution'] = {'type': '', 'description': ''}
        self.fields['isrn'] = {'type': '', 'description': ''}

        self.current_values = dict()

        self.view = view.BibTeXWizardView(self.main_window)

        self.is_not_setup = True
        self.document_type_set = False

    def run(self, dialog_type, document):
        self.document = document

        if self.is_not_setup:
            self.create_pages_and_add_them_to_view()
            self.init_current_values()
            self.setup()
            self.is_not_setup = False

        titles = {'new_entry': _('Create a new BibTeX Entry'), 'previous_entries': _('Add BibTeX Entry'), 'search_online': _('Add BibTeX Entry')}
        self.view.headerbar.set_title(titles[dialog_type])
        self.view.create_button.set_sensitive(False)

        self.presets = None
        self.current_page = 0
        self.load_presets()
        self.goto_page(0)

        response = self.view.run()

        if response == Gtk.ResponseType.APPLY:
            self.save_presets()
            self.insert_template()

        self.view.dialog.hide()

    def create_pages_and_add_them_to_view(self):
        self.pages = list()
        self.pages.append(CreateNewEntryPage(self, self.document_types, self.current_values))
        self.fields_entry_page = FieldsEntryPage(self, self.current_values)
        self.pages.append(self.fields_entry_page)
        for page in self.pages: self.view.notebook.append_page(page.view)

    def init_current_values(self):
        self.current_values['document_type'] = 'article'
        self.current_values['identifier'] = ''
        self.current_values['fields'] = dict()
        for field in self.fields.keys():
            self.current_values['fields'][field] = ''
    
    def setup(self):
        self.view.dialog.connect('key-press-event', self.on_keypress)
        for page in self.pages: page.observe_view()
        self.view.next_button.connect('clicked', self.goto_page_next)
        self.view.back_button.connect('clicked', self.goto_page_prev)

    def load_presets(self):
        if self.presets == None:
            presets = self.settings.get_value('app_bibtex_wizard', 'presets')
            if presets != None: self.presets = pickle.loads(presets)

        for page in self.pages:
            page.load_presets(self.presets)

    def save_presets(self):
        presets = dict()
        presets['document_type'] = self.current_values['document_type']
        presets['identifier'] = self.current_values['identifier']
        presets['include_empty_optional'] = self.fields_entry_page.view.option_include_empty.get_active()
        self.settings.set_value('app_bibtex_wizard', 'presets', pickle.dumps(presets))

    def goto_page_next(self, button=None, data=None):
        self.goto_page(1)

    def goto_page_prev(self, button=None, data=None):
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
        else:
            self.view.next_button.hide()
            self.view.back_button.show_all()
            self.view.create_button.show_all()

    def on_keypress(self, widget, event, data=None):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.keyval == Gdk.keyval_from_name('Return'):
            if event.state & modifiers == 0:
                if self.current_page in range(0, 1):
                    self.view.next_button.clicked()
                    return True
                elif self.current_page == 1:
                    if self.view.create_button.get_sensitive():
                        self.view.create_button.clicked()
                        return True
        return False

    def check_required_fields(self):
        if len(self.fields_entry_page.blank_required_fields) > 0:
            self.view.create_button.set_sensitive(False)
        else:
            self.view.create_button.set_sensitive(True)

    def set_document_type(self, document_type):
        if self.current_values['document_type'] != document_type or not self.document_type_set:
            self.document_type_set = True
            self.current_values['document_type'] = document_type
            attributes = self.document_types[document_type]

            for entry in self.fields_entry_page.view.required_fields_entries.get_children():
                self.fields_entry_page.view.required_fields_entries.remove(entry)
            self.fields_entry_page.required_fields = list()
            view = self.fields_entry_page.view.identifier_entry
            self.fields_entry_page.view.required_fields_entries.pack_start(view, False, False, 0)
            view.show_all()
            for required_field in attributes['fields_required']:
                view = self.fields_entry_page.view.required_entry_views[required_field]
                self.fields_entry_page.view.required_fields_entries.pack_start(view, False, False, 0)
                view.show_all()
                self.fields_entry_page.required_fields.append(required_field)
            self.fields_entry_page.required_fields.append('identifier')
            self.fields_entry_page.blank_required_fields = self.fields_entry_page.required_fields.copy()

            for entry in self.fields_entry_page.view.optional_fields_entries.get_children():
                self.fields_entry_page.view.optional_fields_entries.remove(entry)
            for optional_field in attributes['fields_optional']:
                view = self.fields_entry_page.view.optional_entry_views[optional_field]
                self.fields_entry_page.view.optional_fields_entries.pack_start(view, False, False, 0)
                view.show_all()
                    
    def insert_template(self, data=None):
        document_type = self.current_values['document_type']
        text = '@' + document_type + '{' + self.current_values['identifier'] + ''

        for field in self.document_types[document_type]['fields_required']:
            value = self.current_values['fields'][field]
            text += ',\n\t' + field + ' '*(16 - len(field)) + '= "' + value + '"'

        for field in self.document_types[document_type]['fields_optional']:
            value = self.current_values['fields'][field]
            if value != '':
                text += ',\n\t' + field + ' '*(16 - len(field)) + '= "' + value + '"'
            elif self.fields_entry_page.view.option_include_empty.get_active():
                text += ',\n\t' + field + ' '*(16 - len(field)) + '= ""'

        text += '\n}\n\n'

        self.document.insert_text(0, 0, text, False)
        self.document.place_cursor(0)
        self.document.content.scroll_cursor_onscreen()


