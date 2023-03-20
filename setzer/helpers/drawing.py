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


def ellipsize_front(ctx, text, max_width):
    if ctx.text_extents(text).width <= max_width: return text
    dots_width = ctx.text_extents('...').width

    upper_bound = len(text)
    lower_bound = 0
    while upper_bound > lower_bound + 1:
        new_bound = (upper_bound + lower_bound) // 2
        if ctx.text_extents(text[new_bound:]).width > max_width - dots_width:
            lower_bound = new_bound
        else:
            upper_bound = new_bound
    return '...' + text[upper_bound:]


def ellipsize_back(ctx, text, max_width):
    if ctx.text_extents(text).width <= max_width: return text
    dots_width = ctx.text_extents('...').width

    upper_bound = len(text)
    lower_bound = 0
    while upper_bound > lower_bound + 1:
        new_bound = (upper_bound + lower_bound) // 2
        if ctx.text_extents(text[:new_bound]).width > max_width - dots_width:
            upper_bound = new_bound
        else:
            lower_bound = new_bound
    return text[:upper_bound] + '...'


