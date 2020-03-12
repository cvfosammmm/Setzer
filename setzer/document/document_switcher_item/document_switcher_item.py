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

import setzer.document.document_switcher_item.document_switcher_item_presenter as document_switcher_item_presenter
import setzer.document.document_switcher_item.document_switcher_item_viewgtk as document_switcher_item_view
from setzer.helpers.observable import Observable


class DocumentSwitcherItem(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document


class DocumentSwitcherItemLaTeX(DocumentSwitcherItem):

    def __init__(self, document):
        DocumentSwitcherItem.__init__(self, document)

        self.view = document_switcher_item_view.OpenDocsPopoverItem(document)
        self.presenter = document_switcher_item_presenter.DocumentSwitcherItemPresenterLaTeX(self.document, self.view)


class DocumentSwitcherItemBibTeX(DocumentSwitcherItem):

    def __init__(self, document):
        DocumentSwitcherItem.__init__(self, document)

        self.view = document_switcher_item_view.OpenDocsPopoverItem(document)
        self.presenter = document_switcher_item_presenter.DocumentSwitcherItemPresenterBibTeX(self.document, self.view)


