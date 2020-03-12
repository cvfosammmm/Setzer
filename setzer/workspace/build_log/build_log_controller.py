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


class BuildLogController(object):
    
    def __init__(self, build_log, build_log_view):
        self.build_log = build_log
        self.view = build_log_view
        self.view.list.connect('row-activated', self.on_build_log_row_activated)

    def on_build_log_row_activated(self, box, row, data=None):
        if self.build_log.document == None: return

        item = row.get_child()
        if item.filename == self.build_log.document.get_filename():
            buff = self.build_log.document.get_buffer()
            if buff != None:
                line_number = item.line_number - 1
                if line_number >= 0:
                    buff.place_cursor(buff.get_iter_at_line(line_number))
                self.build_log.document.view.source_view.scroll_mark_onscreen(buff.get_insert())
                self.build_log.document.view.source_view.grab_focus()
        else:
            if item.filename != None:
                document_candidate = self.build_log.workspace.get_document_by_filename(item.filename)
                if document_candidate != None:
                    self.build_log.workspace.set_active_document(document_candidate)
                else:
                    self.build_log.workspace.create_document_from_filename(item.filename, True)
                buff = self.build_log.workspace.active_document.get_buffer()
                if buff != None:
                    line_number = item.line_number - 1
                    if line_number >= 0:
                        buff.place_cursor(buff.get_iter_at_line(line_number))
                    self.build_log.workspace.active_document.view.source_view.scroll_mark_onscreen(buff.get_insert())
                    self.build_log.workspace.active_document.view.source_view.grab_focus()


