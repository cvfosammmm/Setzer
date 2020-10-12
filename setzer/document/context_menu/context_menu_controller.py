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


class ContextMenuController(object):
    
    def __init__(self, context_menu, scbar_view):
        scbar_view.model_button_undo.connect('clicked', context_menu.on_undo)
        scbar_view.model_button_redo.connect('clicked', context_menu.on_redo)
        scbar_view.model_button_cut.connect('clicked', context_menu.on_cut)
        scbar_view.model_button_copy.connect('clicked', context_menu.on_copy)
        scbar_view.model_button_paste.connect('clicked', context_menu.on_paste)
        scbar_view.model_button_delete.connect('clicked', context_menu.on_delete)
        scbar_view.model_button_select_all.connect('clicked', context_menu.on_select_all)

        if context_menu.document.is_latex_document():
            scbar_view.model_button_toggle_comment.connect('clicked', context_menu.on_toggle_comment)
            scbar_view.model_button_show_in_preview.connect('clicked', context_menu.on_show_in_preview)


