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


class Observable(object):
    ''' Can send observers messages if the inheriting class has
        changed. Observers can register with the classes and
        get change notifications pushed to them. '''

    def __init__(self):
        self.observers = set()
    
    def add_change_code(self, change_code, parameter):
        ''' Observables call this method to notify observers of
            changes in their states. '''
        
        for observer in self.observers:
            observer.change_notification(change_code, self, parameter)
    
    def register_observer(self, observer):
        ''' Observer call this method to register themselves with observable
            objects. They have themselves to implement a method
            'change_notification(change_code, parameter)' which the observable
            will call when it's state changes. '''
        
        self.observers.add(observer)



