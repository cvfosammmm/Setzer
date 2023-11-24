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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import GLib

from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.helpers.popover import Popover


class MathMenu(object):

    def __init__(self, popover_manager):
        self.view = MathMenuView(popover_manager)


class MathMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(288)

        self.add_action_button('main', _('Include AMS Packages'), 'win.add-packages', GLib.Variant('as', ['amsmath', 'amssymb', 'amsfonts', 'amsthm']))
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_before_after_item('main', _('Inline Math Section') + ' ($ ... $)', ['$ ', ' $'], shortcut=_('Ctrl') + '+M')
        self.add_before_after_item('main', _('Display Math Section') + ' (\\[ ... \\])', ['\\[ ', ' \\]'], shortcut=_('Shift') + '+Ctrl' + '+M')
        self.add_menu_button(_('Math Environments'), 'math_environments')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_before_after_item('main', _('Subscript') + ' (_{})', ['_{', '}'], shortcut=_('Shift') + '+' + _('Ctrl') + '+D')
        self.add_before_after_item('main', _('Superscript') + ' (^{})', ['^{', '}'], shortcut=_('Shift') + '+' + _('Ctrl') + '+U')
        self.add_insert_symbol_item('main', _('Fraction') + ' (\\frac)', ['\\frac{•}{•}'], shortcut=_('Shift') + '+Alt' + '+F')
        self.add_before_after_item('main', _('Square Root') + ' (\\sqrt)', ['\\sqrt{', '}'])
        self.add_insert_symbol_item('main', '\\left', ['\\left •'], shortcut=_('Shift') + '+' + _('Ctrl') + '+L')
        self.add_insert_symbol_item('main', '\\right', ['\\right •'], shortcut=_('Shift') + '+' + _('Ctrl') + '+R')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_menu_button(_('Math Functions'), 'math_functions')
        self.add_menu_button(_('Math Font Styles'), 'math_font_styles')
        self.add_menu_button(_('Math Stacking Symbols'), 'math_stacking_symbols')
        self.add_menu_button(_('Math Accents'), 'math_accents')
        self.add_menu_button(_('Math Spaces'), 'math_spaces')

        # submenu: math environments
        self.add_page('math_environments', _('Math Environments'))

        self.add_before_after_item('math_environments', 'equation', ['\\begin{equation}\n\t', '\n\\end{equation}'], shortcut=_('Shift') + '+' + _('Ctrl') + '+N')
        self.add_before_after_item('math_environments', 'equation*', ['\\begin{equation*}\n\t', '\n\\end{equation*}'])
        self.add_before_after_item('math_environments', 'align', ['\\begin{align}\n\t', '\n\\end{align}'])
        self.add_before_after_item('math_environments', 'align*', ['\\begin{align*}\n\t', '\n\\end{align*}'])
        self.add_before_after_item('math_environments', 'alignat', ['\\begin{alignat}\n\t', '\n\\end{alignat}'])
        self.add_before_after_item('math_environments', 'alignat*', ['\\begin{alignat*}\n\t', '\n\\end{alignat*}'])
        self.add_before_after_item('math_environments', 'flalign', ['\\begin{flalign}\n\t', '\n\\end{flalign}'])
        self.add_before_after_item('math_environments', 'flalign*', ['\\begin{flalign*}\n\t', '\n\\end{flalign*}'])
        self.add_before_after_item('math_environments', 'gather', ['\\begin{gather}\n\t', '\n\\end{gather}'])
        self.add_before_after_item('math_environments', 'gather*', ['\\begin{gather*}\n\t', '\n\\end{gather*}'])
        self.add_before_after_item('math_environments', 'multline', ['\\begin{multline}\n\t', '\n\\end{multline}'])
        self.add_before_after_item('math_environments', 'multline*', ['\\begin{multline*}\n\t', '\n\\end{multline*}'])

        # submenu: math functions
        self.add_page('math_functions', _('Math Functions'))
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.set_hexpand(True)
        for math_function in ['arccos', 'arcsin', 'arctan', 'cos', 'cosh', 'cot', 'coth', 'csc', 'deg', 'det', 'dim', 'exp', 'gcd', 'hom', 'inf']:
            button = MenuBuilder.create_button('\\' + math_function)
            button.set_action_name('win.insert-symbol')
            button.set_action_target_value(GLib.Variant('as', ['\\' + math_function + ' ']))
            button.connect('clicked', self.on_closing_button_click)
            self.register_button_for_keyboard_navigation(button, pagename='math_functions')
            vbox.append(button)
        hbox.append(vbox)
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.set_hexpand(True)
        for math_function in ['ker', 'lg', 'lim', 'liminf', 'limsup', 'ln', 'log', 'max', 'min', 'sec', 'sin', 'sinh', 'sup', 'tan', 'tanh']:
            button = MenuBuilder.create_button('\\' + math_function)
            button.set_action_name('win.insert-symbol')
            button.set_action_target_value(GLib.Variant('as', ['\\' + math_function + ' ']))
            button.connect('clicked', self.on_closing_button_click)
            self.register_button_for_keyboard_navigation(button, pagename='math_functions')
            vbox.append(button)
        hbox.append(vbox)
        self.add_widget(hbox, 'math_functions')

        # submenu: math font styles
        self.add_page('math_font_styles', _('Math Font Styles'))
        self.add_before_after_item('math_font_styles', _('Bold') + ' (\\mathbf)', ['\\mathbf{', '}'], icon='menu-math-font-styles-1-symbolic')
        self.add_before_after_item('math_font_styles', _('Italic') + ' (\\mathit)', ['\\mathit{', '}'], icon='menu-math-font-styles-2-symbolic')
        self.add_before_after_item('math_font_styles', _('Roman') + ' (\\mathrm)', ['\\mathrm{', '}'], icon='menu-math-font-styles-3-symbolic')
        self.add_before_after_item('math_font_styles', _('Sans Serif') + ' (\\mathsf)', ['\\mathsf{', '}'], icon='menu-math-font-styles-4-symbolic')
        self.add_before_after_item('math_font_styles', _('Typewriter') + ' (\\mathtt)', ['\\mathtt{', '}'], icon='menu-math-font-styles-5-symbolic')
        self.add_before_after_item('math_font_styles', _('Calligraphic') + ' (\\mathcal)', ['\\mathcal{', '}'], icon='menu-math-font-styles-6-symbolic')
        self.add_before_after_item('math_font_styles', _('Blackboard Bold') + ' (\\mathbb)', ['\\mathbb{', '}'], icon='menu-math-font-styles-7-symbolic')
        self.add_before_after_item('math_font_styles', _('Fraktur') + ' (\\mathfrak)', ['\\mathfrak{', '}'], icon='menu-math-font-styles-8-symbolic')

        # submenu: math stacking symbols
        self.add_page('math_stacking_symbols', _('Math Stacking Symbols'))
        self.add_before_after_item('math_stacking_symbols', '\\overline{}', ['\\overline{', '}'])
        self.add_before_after_item('math_stacking_symbols', '\\underline{}', ['\\underline{', '}'])
        self.add_before_after_item('math_stacking_symbols', '\\overbrace{}', ['\\overbrace{', '}'])
        self.add_before_after_item('math_stacking_symbols', '\\underbrace{}', ['\\underbrace{', '}'])
        self.add_before_after_item('math_stacking_symbols', '\\overleftarrow{}', ['\\overleftarrow{', '}'])
        self.add_before_after_item('math_stacking_symbols', '\\overrightarrow{}', ['\\overrightarrow{', '}'])
        self.add_before_after_item('math_stacking_symbols', '\\stackrel{}{}', ['\\stackrel{•}{', '}'])
        self.add_before_after_item('math_stacking_symbols', '\\overset{}{}', ['\\overset{•}{', '}'])
        self.add_before_after_item('math_stacking_symbols', '\\underset{}{}', ['\\underset{•}{', '}'])
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), 'math_stacking_symbols')
        self.add_before_after_item('math_stacking_symbols', 'cases', ['\\begin{cases}\n\t', '\n\\end{cases}'])
        self.add_before_after_item('math_stacking_symbols', 'split', ['\\begin{split}\n\t', '\n\\end{split}'])

        # submenu: math accents
        self.add_page('math_accents', _('Math Accents'))
        self.add_before_after_item('math_accents', '\\dot{}', ['\\dot{', '}'], icon='menu-math-accents-1-symbolic')
        self.add_before_after_item('math_accents', '\\ddot{}', ['\\ddot{', '}'], icon='menu-math-accents-2-symbolic')
        self.add_before_after_item('math_accents', '\\vec{}', ['\\vec{', '}'], icon='menu-math-accents-3-symbolic')
        self.add_before_after_item('math_accents', '\\bar{}', ['\\bar{', '}'], icon='menu-math-accents-4-symbolic')
        self.add_before_after_item('math_accents', '\\tilde{}', ['\\tilde{', '}'], icon='menu-math-accents-5-symbolic')
        self.add_before_after_item('math_accents', '\\hat{}', ['\\hat{', '}'], icon='menu-math-accents-6-symbolic')
        self.add_before_after_item('math_accents', '\\check{}', ['\\check{', '}'], icon='menu-math-accents-7-symbolic')
        self.add_before_after_item('math_accents', '\\breve{}', ['\\breve{', '}'], icon='menu-math-accents-8-symbolic')
        self.add_before_after_item('math_accents', '\\acute{}', ['\\acute{', '}'], icon='menu-math-accents-9-symbolic')
        self.add_before_after_item('math_accents', '\\grave{}', ['\\grave{', '}'], icon='menu-math-accents-10-symbolic')

        # submenu: math spaces
        self.add_page('math_spaces', _('Math Spaces'))
        self.add_insert_symbol_item('math_spaces', 'Negative', ['\\!'])
        self.add_insert_symbol_item('math_spaces', 'Thin', ['\\,'])
        self.add_insert_symbol_item('math_spaces', 'Medium', ['\\:'])
        self.add_insert_symbol_item('math_spaces', 'Thick', ['\\;'])
        self.add_insert_symbol_item('math_spaces', 'Interword', ['\\ '])
        self.add_insert_symbol_item('math_spaces', 'Enspace', ['\\enspace '])
        self.add_insert_symbol_item('math_spaces', 'One Quad', ['\\quad '])
        self.add_insert_symbol_item('math_spaces', 'Two Quads', ['\\qquad '])


