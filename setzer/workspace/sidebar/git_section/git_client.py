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
from gi.repository import Gio, GLib

import shutil
import urllib.parse


# credentials are never stored by Setzer itself, they are handed over to git's
# own credential helpers. this config keeps them in git-credential-cache
# (memory only, gone after the timeout) when the user doesn't want them saved.
cache_helper = 'cache --timeout=900'


class GitClient(object):
    ''' Runs git commands asynchronously on the main loop. No GTK in here. '''

    def __init__(self):
        self.git_path = shutil.which('git')

    def is_available(self):
        return self.git_path != None

    def run(self, arguments, cwd, callback=None, stdin=None, config=None):
        ''' callback is called with (exit_code, stdout, stderr), exit_code is
            -1 when git could not be started at all. '''

        if self.git_path == None:
            if callback != None: callback(-1, '', _('git is not installed.'))
            return

        flags = Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE
        if stdin != None:
            flags |= Gio.SubprocessFlags.STDIN_PIPE

        launcher = Gio.SubprocessLauncher.new(flags)
        launcher.set_cwd(cwd)

        # never let git block on a terminal that isn't there, and keep its
        # output parseable no matter which locale the user runs in.
        launcher.setenv('GIT_TERMINAL_PROMPT', '0', True)
        launcher.setenv('GIT_OPTIONAL_LOCKS', '0', True)
        launcher.setenv('LC_ALL', 'C', True)
        launcher.unsetenv('GIT_ASKPASS')
        launcher.unsetenv('SSH_ASKPASS')

        argv = [self.git_path] + (config if config != None else []) + arguments

        try: process = launcher.spawnv(argv)
        except GLib.Error as error:
            if callback != None: callback(-1, '', error.message)
            return

        # communicate_utf8 would cut the output at the first NUL byte, which is
        # exactly what "git status -z" separates its records with
        stdin_bytes = GLib.Bytes.new(stdin.encode('utf-8')) if stdin != None else None
        process.communicate_async(stdin_bytes, None, self.on_process_finished, callback)

    def on_process_finished(self, process, result, callback):
        try: _unused, stdout, stderr = process.communicate_finish(result)
        except GLib.Error as error:
            if callback != None: callback(-1, '', error.message)
            return

        if callback != None:
            callback(process.get_exit_status(), decode(stdout), decode(stderr))

    def get_config(self, remember):
        ''' Config for network operations. An empty credential.helper value
            resets the helper list, so when the user doesn't want to store the
            password the persistent helpers never see it. '''

        if remember:
            return ['-c', 'credential.helper=' + cache_helper]
        else:
            return ['-c', 'credential.helper=', '-c', 'credential.helper=' + cache_helper]


def decode(data):
    if data == None: return ''
    return data.get_data().decode('utf-8', errors='replace')


def is_auth_failure(stderr):
    markers = ['could not read Username', 'could not read Password',
               'Authentication failed', 'terminal prompts disabled',
               'Invalid username or password', 'Invalid username or token']
    return any(marker in stderr for marker in markers)


def parse_remote_url(url):
    ''' Returns the credential description for an http(s) remote, or None for
        remotes that don't use git's credential system (ssh, local paths). '''

    if url == None: return None
    url = url.strip()
    if not url.startswith('http://') and not url.startswith('https://'): return None

    parts = urllib.parse.urlsplit(url)
    if parts.hostname == None: return None

    host = parts.hostname
    if parts.port != None:
        host += ':' + str(parts.port)

    description = {'protocol': parts.scheme, 'host': host, 'path': parts.path.strip('/')}
    if parts.username not in [None, '']:
        description['username'] = urllib.parse.unquote(parts.username)
    return description


def format_credential_request(description, username=None, password=None):
    lines = list()
    for key in ['protocol', 'host', 'path']:
        if description.get(key, '') != '':
            lines.append(key + '=' + description[key])
    if username not in [None, '']:
        lines.append('username=' + username)
    elif description.get('username', '') != '':
        lines.append('username=' + description['username'])
    if password not in [None, '']:
        lines.append('password=' + password)
    return '\n'.join(lines) + '\n\n'
