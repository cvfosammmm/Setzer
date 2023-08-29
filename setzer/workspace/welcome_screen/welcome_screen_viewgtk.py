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


class WelcomeScreenView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)

        self.drawing_area = Gtk.DrawingArea()
        self.overlay = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.overlay.set_hexpand(True)
        self.overlay.get_style_context().add_class('welcome')
        self.header = Gtk.Label.new(_('Write beautiful LaTeX documents with ease!'))
        self.header.set_wrap(True)
        self.header.get_style_context().add_class('welcome-header')
        self.description = Gtk.Label.new(_('Click the open or create buttons in the headerbar above to start editing.'))
        self.description.set_wrap(True)
        self.description.get_style_context().add_class('welcome-description')
        self.overlay.append(self.header)
        self.overlay.append(self.description)
        self.overlay.set_valign(Gtk.Align.CENTER)

        self.hbox = Gtk.CenterBox()
        self.hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.hbox.set_center_widget(self.overlay)

        self.set_child(self.drawing_area)
        self.add_overlay(self.hbox)

        self.text = list()
        self.text.append('Reiciendis libero nemo sint autem. Maxime et ea qui provident. Sunt nihil eaque quidem dolores sequi debitis. Temporibus quia ut fuga sint pariatur aut.')
        self.text.append('Autem dolore aut quo in qui. Aut dolor dignissimos laborum eum perspiciatis iusto et veniam. Voluptate ea pariatur omnis qui eum ab est. Sequi ut sint rerum et.')
        self.text.append('Dolore nulla sunt corporis voluptatum dolore reprehenderit. Molestiae est unde sint facere iusto ea impedit. Soluta temporibus mollitia totam id earum. At inventore amet omnis. Dignissimos itaque perspiciatis dolore.')
        self.text.append('Illum et molestias quia provident. Dolores aut quis molestiae cumque. Unde dignissimos placeat possimus. Sit et ullam quia deserunt illo inventore. Id modi quidem fugit fuga magni possimus praesentium.')
        self.text.append('Aliquid commodi qui tempore et. Tempora ullam quod nisi eum dolores voluptatem quia culpa. Provident et voluptate dignissimos aliquam qui aut ratione. Dolorum qui qui nostrum consequatur.')
        self.text.append('Saepe perspiciatis ducimus vitae suscipit eligendi mollitia. Delectus quo praesentium ut sit. Dolor non aliquid maiores enim minus. Exercitationem mollitia quia et atque itaque. Doloremque voluptas esse debitis similique. Repellendus qui doloribus aut ea quod perferendis libero autem.')
        self.text.append('Architecto qui sit quis voluptatem. Est nobis modi deleniti ullam sunt eum quia sed. Expedita asperiores odit dicta quam ut. Ratione qui qui hic quia eligendi sed qui.')
        self.text.append('Natus et eum velit eveniet assumenda delectus nihil. Non eligendi vitae voluptatum nihil omnis ex molestiae. Excepturi velit dignissimos ut quia quae nemo. Maxime laborum in ad repellendus dolore qui repudiandae et. Sed laudantium non nesciunt.')
        self.text.append('Consectetur qui sed autem expedita aut quae aut. Qui et sit sit aliquam consequatur sed esse est. Provident dolorem facere libero voluptas est voluptatem sed.')
        self.text.append('Ullam non esse et ex alias sunt aut. Eaque beatae et veritatis. Est consequatur exercitationem illo repudiandae magni. Qui aspernatur quasi placeat qui veritatis dolores. Assumenda et nobis hic.')
        self.text.append('Reiciendis libero nemo sint autem. Maxime et ea qui provident. Sunt nihil eaque quidem dolores sequi debitis. Temporibus quia ut fuga sint pariatur aut.')
        self.text.append('Autem dolore aut quo in qui. Aut dolor dignissimos laborum eum perspiciatis iusto et veniam. Voluptate ea pariatur omnis qui eum ab est. Sequi ut sint rerum et.')
        self.text.append('Dolore nulla sunt corporis voluptatum dolore reprehenderit. Molestiae est unde sint facere iusto ea impedit. Soluta temporibus mollitia totam id earum. At inventore amet omnis. Dignissimos itaque perspiciatis dolore.')
        self.text.append('Illum et molestias quia provident. Dolores aut quis molestiae cumque. Unde dignissimos placeat possimus. Sit et ullam quia deserunt illo inventore. Id modi quidem fugit fuga magni possimus praesentium.')
        self.text.append('Aliquid commodi qui tempore et. Tempora ullam quod nisi eum dolores voluptatem quia culpa. Provident et voluptate dignissimos aliquam qui aut ratione. Dolorum qui qui nostrum consequatur.')
        self.text.append('Saepe perspiciatis ducimus vitae suscipit eligendi mollitia. Delectus quo praesentium ut sit. Dolor non aliquid maiores enim minus. Exercitationem mollitia quia et atque itaque. Doloremque voluptas esse debitis similique. Repellendus qui doloribus aut ea quod perferendis libero autem.')
        self.text.append('Architecto qui sit quis voluptatem. Est nobis modi deleniti ullam sunt eum quia sed. Expedita asperiores odit dicta quam ut. Ratione qui qui hic quia eligendi sed qui.')
        self.text.append('Natus et eum velit eveniet assumenda delectus nihil. Non eligendi vitae voluptatum nihil omnis ex molestiae. Excepturi velit dignissimos ut quia quae nemo. Maxime laborum in ad repellendus dolore qui repudiandae et. Sed laudantium non nesciunt.')
        self.text.append('Consectetur qui sed autem expedita aut quae aut. Qui et sit sit aliquam consequatur sed esse est. Provident dolorem facere libero voluptas est voluptatem sed.')
        self.text.append('Ullam non esse et ex alias sunt aut. Eaque beatae et veritatis. Est consequatur exercitationem illo repudiandae magni. Qui aspernatur quasi placeat qui veritatis dolores. Assumenda et nobis hic.')
        self.text.append('Reiciendis libero nemo sint autem. Maxime et ea qui provident. Sunt nihil eaque quidem dolores sequi debitis. Temporibus quia ut fuga sint pariatur aut.')
        self.text.append('Autem dolore aut quo in qui. Aut dolor dignissimos laborum eum perspiciatis iusto et veniam. Voluptate ea pariatur omnis qui eum ab est. Sequi ut sint rerum et.')
        self.text.append('Dolore nulla sunt corporis voluptatum dolore reprehenderit. Molestiae est unde sint facere iusto ea impedit. Soluta temporibus mollitia totam id earum. At inventore amet omnis. Dignissimos itaque perspiciatis dolore.')
        self.text.append('Illum et molestias quia provident. Dolores aut quis molestiae cumque. Unde dignissimos placeat possimus. Sit et ullam quia deserunt illo inventore. Id modi quidem fugit fuga magni possimus praesentium.')
        self.text.append('Aliquid commodi qui tempore et. Tempora ullam quod nisi eum dolores voluptatem quia culpa. Provident et voluptate dignissimos aliquam qui aut ratione. Dolorum qui qui nostrum consequatur.')
        self.text.append('Saepe perspiciatis ducimus vitae suscipit eligendi mollitia. Delectus quo praesentium ut sit. Dolor non aliquid maiores enim minus. Exercitationem mollitia quia et atque itaque. Doloremque voluptas esse debitis similique. Repellendus qui doloribus aut ea quod perferendis libero autem.')
        self.text.append('Architecto qui sit quis voluptatem. Est nobis modi deleniti ullam sunt eum quia sed. Expedita asperiores odit dicta quam ut. Ratione qui qui hic quia eligendi sed qui.')
        self.text.append('Natus et eum velit eveniet assumenda delectus nihil. Non eligendi vitae voluptatum nihil omnis ex molestiae. Excepturi velit dignissimos ut quia quae nemo. Maxime laborum in ad repellendus dolore qui repudiandae et. Sed laudantium non nesciunt.')
        self.text.append('Consectetur qui sed autem expedita aut quae aut. Qui et sit sit aliquam consequatur sed esse est. Provident dolorem facere libero voluptas est voluptatem sed.')
        self.text.append('Ullam non esse et ex alias sunt aut. Eaque beatae et veritatis. Est consequatur exercitationem illo repudiandae magni. Qui aspernatur quasi placeat qui veritatis dolores. Assumenda et nobis hic.')


