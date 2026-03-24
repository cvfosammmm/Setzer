#!/usr/bin/env python3
# coding: utf-8

# Note: For non-literal characters, use their descriptive names.
# This is required for correct parsing by the GTK shortcut system.
#
# | Character   | Name       |
# | ----------- | ---------- |
# | ?           | question   |
# | /           | slash      |
# | +           | plus       |
# | =           | equal      |
# | -           | minus      |
# | "           | quotedbl   |
# | Tab         | Tab        |
# | Enter       | Return     |
# | Esc         | Escape     |
# | Space (` `) | space      |

DEFAULT_KEYBINDS = {
    'app': {
        'new-latex-document': ['Ctrl', 'N'],
        'open-document-dialog': ['Ctrl', 'O'],
        'save': ['Ctrl', 'S'],
        'save-as': ['Ctrl', 'Shift', 'S'],
        'close-active-document': ['Ctrl', 'W'],
        'quit': ['Ctrl', 'Q'],
        'show-shortcuts-dialog': ['Ctrl', 'question'],
        'shortcut_show_open_docs': ['Ctrl', 'P'],
        'shortcut_switch_document': ['Ctrl', 'Tab'],
        'shortcut_show_document_chooser': ['Ctrl', 'Shift', 'P'],
        'zoom-in': ['Ctrl', 'equal'], # As in US keyboard, shift + equal is plus
        'zoom-out': ['Ctrl', 'minus'],
        'reset-zoom': ['Ctrl', '0'],
        'start-search': ['Ctrl', 'F'],
        'start-search-and-replace': ['Ctrl', 'H'],
        'find-next': ['F3'],
        'find-previous': ['Shift', 'F3'],
        'shortcut_help': ['F1'],
        'shortcut_document_structure_toggle': ['F2'],
        'shortcut_symbols_toggle': ['Alt', 'Y'],
        'save-and-build': ['Ctrl', 'Alt', 'B'],
        'build': ['F6'],
        'forward-sync': ['Ctrl', 'Alt', 'J'],
        'shortcut_build_log': ['F8'],
        'shortcut_preview': ['Ctrl', 'Alt', 'V'],
        'shortcut_show_hamburger': ['F10']
    },
    'document': {
        'cut': ['Ctrl', 'X'],
        'copy': ['Ctrl', 'C'],
        'paste': ['Ctrl', 'V'],
        'select-all': ['Ctrl', 'A'],
        'undo': ['Ctrl', 'Z'],
        'redo': ['Ctrl', 'Shift', 'Z'],
        'redo_alt': ['Ctrl', 'Y'],
        'show-context-menu': ['F12'],
        'toggle-insert': ['Insert'],
        'move-line-up': ['Alt', 'Up'],
        'move-line-down': ['Alt', 'Down'],
        'move-word-left': ['Alt', 'Left'],
        'move-word-right': ['Alt', 'Right'],
        'increment-number': ['Ctrl', 'Shift', 'A'],
        'decrement-number': ['Ctrl', 'Shift', 'X'],
        'search-next': ['Ctrl', 'G'],
        'search-previous': ['Ctrl', 'Shift', 'G'],
        'select-next-placeholder': ['Tab'],
        'select-previous-placeholder': ['Shift', 'Tab']
    },
    'latex': {
        'toggle-comment': ['Ctrl', 'slash'],
        'shortcut_quotes': ['Ctrl', 'quotedbl']
    },
    'latex-before-after': {
        '\\\\textbf{@@}': ['Ctrl', 'B'],
        '\\\\textit{@@}': ['Ctrl', 'I'],
        '\\\\underline{@@}': ['Ctrl', 'U'],
        '\\\\texttt{@@}': ['Ctrl', 'Shift', 'T'],
        '\\\\emph{@@}': ['Ctrl', 'Shift', 'E'],
        '$ @@ $': ['Ctrl', 'M'],
        '\\\\[ @@ \\\\]': ['Ctrl', 'Shift', 'M'],
        '\\\\begin{equation}\\n\\t@@\\n\\\\end{equation}': ['Ctrl', 'Shift', 'N'],
        '\\\\begin{•}\\n\\t@@\\n\\\\end{•}': ['Ctrl', 'E'],
        '_{@@}': ['Ctrl', 'Shift', 'D'],
        '^{@@}': ['Ctrl', 'Shift', 'U']
    },
    'latex-symbol': {
        '\\\\frac{•}{•}': ['Alt', 'Shift', 'F'],
        '\\\\left •': ['Ctrl', 'Shift', 'L'],
        '\\\\right •': ['Ctrl', 'Shift', 'R'],
        '\\\\item •': ['Ctrl', 'Shift', 'I'],
        '\\\\\\\\\\n': ['Ctrl', 'Return']
    }
}
