#!/usr/bin/env python3
# coding: utf-8

import json
import os
from setzer.app.service_locator import ServiceLocator
from setzer.keyboard_shortcuts.defaults import DEFAULT_KEYBINDS

class KeybindParser:
    _keybinds = None

    @classmethod
    def load_keybinds(cls):
        if cls._keybinds is not None:
            return
            
        try:
            # Initialize with a deep copy of defaults
            cls._keybinds = {cat: dict(binds) for cat, binds in DEFAULT_KEYBINDS.items()}
        except Exception:
            cls._keybinds = {}
            return
        
        config_path = ServiceLocator.get_keymap_config_path()
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'keybinds' in data and isinstance(data['keybinds'], dict):
                        # Merge config into defaults
                        for category, binds in data['keybinds'].items():
                            if category in cls._keybinds and isinstance(binds, dict):
                                cls._keybinds[category].update(binds)
            except Exception as e:
                print(f"Failed to load keybinds from config file {config_path}: {e}")
                # Reset to defaults if merging partially failed or corrupted state
                cls._keybinds = {cat: dict(binds) for cat, binds in DEFAULT_KEYBINDS.items()}

    @classmethod
    def get_category_keybinds(cls, category):
        cls.load_keybinds()
        return cls._keybinds.get(category, {})

    @classmethod
    def get_shortcut(cls, action_name, category=None):
        cls.load_keybinds()
        if category:
            return cls._keybinds.get(category, {}).get(action_name)
        
        for cat_binds in cls._keybinds.values():
            if action_name in cat_binds:
                return cat_binds[action_name]
        return None

    @classmethod
    def to_gtk(cls, shortcut):
        """Converts ['Ctrl', 'S'] to '<Control>s'"""
        if not isinstance(shortcut, list):
            return shortcut
            
        result = ""
        for key in shortcut:
            if key == 'Ctrl':
                result += '<Control>'
            elif key == 'Shift':
                result += '<Shift>'
            elif key == 'Alt':
                result += '<Alt>'
            elif key == 'Super':
                result += '<Super>'
            else:
                result += key
        return result

    @classmethod
    def to_gtk_display(cls, shortcut):
        """Converts ['Ctrl', 'S'] to '<Control>s'"""
        if not isinstance(shortcut, list):
            return shortcut
            
        result = KeybindParser.to_gtk(shortcut).replace('<', '&lt;').replace('>', '&gt;')
        return result

    @classmethod
    def to_display(cls, shortcut):
        """Converts a shortcut array like ['Ctrl', 'slash'] to 'Ctrl+'/'"""
        if not isinstance(shortcut, list):
            return str(shortcut)
        
        formatted_keys = []
        for i, key in enumerate(shortcut):
            display_key = key
            original_key_val = key # Store original to check for replacements later

            # Apply specific key name conversions
            display_key = display_key.replace('slash', "'/'")
            display_key = display_key.replace('question', "'?'")
            display_key = display_key.replace('plus', "'+'")
            display_key = display_key.replace('minus', "'-'")
            display_key = display_key.replace('quotedbl', "'\"'")
            display_key = display_key.replace('Return', _('Enter'))

            # Capitalize single letters after a modifier, if not a modifier itself
            # Modifiers are typically 'Ctrl', 'Shift', 'Alt', 'Super'
            if len(display_key) == 1 and display_key.isalpha() and i > 0 and \
               shortcut[i-1] in ['Ctrl', 'Shift', 'Alt', 'Super']: 
                formatted_keys.append(display_key.upper())
            else:
                formatted_keys.append(display_key)
        
        return "+".join(formatted_keys)
