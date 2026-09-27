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
from gi.repository import GObject

import os.path

import setzer.workspace.sidebar.git_section.git_client as git_client
import setzer.workspace.sidebar.git_section.git_section_viewgtk as git_section_viewgtk
import setzer.workspace.sidebar.git_section.git_section_presenter as git_section_presenter
import setzer.workspace.sidebar.git_section.git_section_controller as git_section_controller
from setzer.dialogs.dialog_locator import DialogLocator
from setzer.helpers.observable import Observable


class GitSection(Observable):

    def __init__(self, workspace, labels):
        Observable.__init__(self)

        self.workspace = workspace
        self.headline_labels = labels
        self.client = git_client.GitClient()

        self.document = None
        self.repo_path = None
        self.branch = None
        self.upstream = None
        self.ahead = 0
        self.behind = 0
        self.last_commit = None
        self.changed_files = list()

        self.busy = None
        self.is_refreshing = False
        self.last_error = None

        self.commit_message = ''
        self.commit_paths = list()
        self.remote_operation = None
        self.credential_description = None
        self.credential_password = None

        self.view = git_section_viewgtk.GitSectionView()
        self.presenter = git_section_presenter.GitSectionPresenter(self)
        self.controller = git_section_controller.GitSectionController(self)

        self.presenter.update()

        if self.client.is_available():
            self.workspace.connect('new_active_document', self.on_new_active_document)
            self.workspace.connect('new_inactive_document', self.on_new_inactive_document)
            GObject.timeout_add(10000, self.on_timeout)
            self.refresh()

    #
    # state
    #

    def on_new_active_document(self, workspace, document):
        document.connect('modified_changed', self.on_modified_changed)
        document.connect('filename_change', self.on_filename_change)
        self.refresh()

    def on_new_inactive_document(self, workspace, document):
        document.disconnect('modified_changed', self.on_modified_changed)
        document.disconnect('filename_change', self.on_filename_change)

    def on_modified_changed(self, document):
        if not document.source_buffer.get_modified():
            self.refresh()

    def on_filename_change(self, document, filename=None):
        self.refresh()

    def on_timeout(self):
        self.refresh()
        return True

    def is_available(self):
        return self.client.is_available()

    def get_working_dir(self):
        document = self.workspace.get_active_document()
        if document == None: return None

        dirname = document.get_dirname()
        if dirname == '' or not os.path.isdir(dirname): return None
        return dirname

    def refresh(self):
        if self.is_refreshing or self.busy != None: return
        if not self.client.is_available(): return

        working_dir = self.get_working_dir()
        if working_dir == None:
            self.reset_state()
            return

        self.is_refreshing = True
        self.client.run(['rev-parse', '--show-toplevel'], working_dir, self.on_toplevel_result)

    def on_toplevel_result(self, exit_code, stdout, stderr):
        if exit_code != 0 or stdout.strip() == '':
            self.is_refreshing = False
            self.reset_state()
            return

        self.repo_path = stdout.strip()
        self.client.run(['status', '--porcelain', '-b', '-z', '-uall'], self.repo_path, self.on_status_result)

    def on_status_result(self, exit_code, stdout, stderr):
        if exit_code != 0:
            self.is_refreshing = False
            self.reset_state()
            return

        self.parse_status(stdout)
        self.client.run(['log', '-1', '--format=%ct%x1f%s%x1f%an'], self.repo_path, self.on_log_result)

    def on_log_result(self, exit_code, stdout, stderr):
        self.is_refreshing = False

        if exit_code != 0 or stdout.strip() == '':
            self.last_commit = None
        else:
            fields = stdout.strip('\n').split('\x1f')
            if len(fields) == 3 and fields[0].isdigit():
                self.last_commit = {'timestamp': int(fields[0]), 'subject': fields[1], 'author': fields[2]}
            else:
                self.last_commit = None

        self.add_change_code('git_state_changed')

    def parse_status(self, stdout):
        self.branch = None
        self.upstream = None
        self.ahead = 0
        self.behind = 0
        changed_files = list()

        records = [record for record in stdout.split('\0') if record != '']
        index = 0
        while index < len(records):
            record = records[index]
            index += 1

            if record.startswith('## '):
                self.parse_branch_header(record[3:])
                continue

            if len(record) < 4: continue
            status = record[:2]
            path = record[3:]
            old_path = None

            # renames and copies are followed by their original path
            if 'R' in status or 'C' in status:
                if index < len(records):
                    old_path = records[index]
                index += 1

            changed_files.append({'status': status, 'path': path, 'old_path': old_path})

        changed_files.sort(key=lambda item: item['path'].lower())
        self.changed_files = changed_files

    def parse_branch_header(self, header):
        if header.startswith('No commits yet on '):
            self.branch = header[len('No commits yet on '):].strip()
            return
        if header.startswith('HEAD (no branch)'):
            self.branch = None
            return

        divergence = ''
        if header.endswith(']') and ' [' in header:
            header, divergence = header.rsplit(' [', 1)
            divergence = divergence[:-1]

        if '...' in header:
            self.branch, self.upstream = header.split('...', 1)
        else:
            self.branch = header

        for part in divergence.split(', '):
            if part.startswith('ahead '): self.ahead = int(part[6:])
            elif part.startswith('behind '): self.behind = int(part[7:])

    def reset_state(self):
        self.repo_path = None
        self.branch = None
        self.upstream = None
        self.ahead = 0
        self.behind = 0
        self.last_commit = None
        self.changed_files = list()
        self.add_change_code('git_state_changed')

    def set_busy(self, operation):
        self.busy = operation
        self.add_change_code('git_state_changed')

    def report_error(self, title, message):
        self.busy = None
        self.last_error = {'title': title, 'message': message.strip()}
        self.add_change_code('git_state_changed')
        self.add_change_code('git_error', self.last_error)

    #
    # operations
    #

    def pull(self):
        if self.repo_path == None or self.busy != None: return

        self.set_busy('pull')
        self.run_remote_operation(['pull', '--ff-only'], self.on_pull_finished)

    def on_pull_finished(self, exit_code, stdout, stderr):
        if exit_code != 0:
            message = stderr.strip() if stderr.strip() != '' else stdout.strip()
            if 'Not possible to fast-forward' in message or 'have diverged' in message:
                message = _('Your branch and the remote branch have diverged. Setzer only does fast forward pulls, please merge or rebase manually.') + '\n\n' + message
            self.report_error(_('Pull failed.'), message)
            return

        self.busy = None
        self.refresh()

    def push(self):
        if self.repo_path == None or self.busy != None: return

        self.set_busy('push')
        self.save_documents_in_repo()
        self.client.run(['status', '--porcelain', '-b', '-z', '-uall'], self.repo_path, self.on_status_before_commit)

    def save_documents_in_repo(self):
        for document in self.workspace.open_documents:
            filename = document.get_filename()
            if filename == None: continue
            if not filename.startswith(self.repo_path + os.sep): continue
            if document.source_buffer.get_modified():
                document.save_to_disk()

    def on_status_before_commit(self, exit_code, stdout, stderr):
        if exit_code != 0:
            self.report_error(_('Push failed.'), stderr)
            return

        self.parse_status(stdout)
        self.add_change_code('git_state_changed')

        if len(self.changed_files) == 0:
            if self.ahead == 0 and self.upstream != None:
                self.busy = None
                self.add_change_code('git_state_changed')
                self.add_change_code('git_info', _('There is nothing to commit and nothing to push.'))
                return
            self.do_push()
            return

        DialogLocator.get_dialog('git_commit').run(self.changed_files, self.on_commit_dialog_response)

    def on_commit_dialog_response(self, response):
        if response == None:
            self.busy = None
            self.add_change_code('git_state_changed')
            return

        self.commit_message = response['message']
        self.commit_paths = response['paths']

        arguments = ['add', '-A', '--'] + self.commit_paths
        self.client.run(arguments, self.repo_path, self.on_add_finished)

    def on_add_finished(self, exit_code, stdout, stderr):
        if exit_code != 0:
            self.report_error(_('Commit failed.'), stderr)
            return

        arguments = ['commit', '-m', self.commit_message, '--'] + self.commit_paths
        self.client.run(arguments, self.repo_path, self.on_commit_finished)

    def on_commit_finished(self, exit_code, stdout, stderr):
        if exit_code != 0:
            message = stderr.strip() if stderr.strip() != '' else stdout.strip()
            self.report_error(_('Commit failed.'), message)
            return

        self.do_push()

    def do_push(self):
        if self.upstream == None and self.branch != None:
            arguments = ['push', '--set-upstream', 'origin', self.branch]
        else:
            arguments = ['push']
        self.run_remote_operation(arguments, self.on_push_finished)

    def on_push_finished(self, exit_code, stdout, stderr):
        if exit_code != 0:
            message = stderr.strip() if stderr.strip() != '' else stdout.strip()
            self.report_error(_('Push failed.'), message)
            return

        self.busy = None
        self.refresh()

    #
    # credentials
    #
    # Setzer never stores credentials itself. On an authentication failure it
    # asks once, hands them to "git credential approve" (which routes them to
    # whichever helper the user has configured) and retries. When the user
    # doesn't want them saved they only go to git-credential-cache.
    #

    def run_remote_operation(self, arguments, callback):
        self.remote_operation = {'arguments': arguments, 'callback': callback, 'retried': False, 'config': None}
        self.client.run(arguments, self.repo_path, self.on_remote_operation_finished)

    def on_remote_operation_finished(self, exit_code, stdout, stderr):
        operation = self.remote_operation

        if exit_code == 0 or not git_client.is_auth_failure(stderr):
            operation['callback'](exit_code, stdout, stderr)
            return

        if operation['retried']:
            self.reject_credentials()
            operation['callback'](exit_code, stdout, stderr)
            return

        self.client.run(['remote', 'get-url', self.get_remote_name()], self.repo_path, self.on_remote_url_result)

    def get_remote_name(self):
        if self.upstream != None and '/' in self.upstream:
            return self.upstream.split('/', 1)[0]
        return 'origin'

    def on_remote_url_result(self, exit_code, stdout, stderr):
        operation = self.remote_operation

        if exit_code != 0:
            operation['callback'](1, '', stderr if stderr.strip() != '' else _('No remote repository is configured.'))
            return

        description = git_client.parse_remote_url(stdout.strip())
        if description == None:
            # ssh and local remotes don't use git's credential system
            operation['callback'](1, '', _('Authentication failed. Setzer can only ask for credentials of remotes using http(s).'))
            return

        self.credential_description = description
        DialogLocator.get_dialog('git_credentials').run(description, self.on_credentials_dialog_response)

    def on_credentials_dialog_response(self, response):
        operation = self.remote_operation

        if response == None:
            self.busy = None
            self.add_change_code('git_state_changed')
            return

        config = self.client.get_config(response['remember'])
        operation['config'] = config
        operation['retried'] = True
        self.credential_description['username'] = response['username']
        self.credential_password = response['password']

        request = git_client.format_credential_request(self.credential_description, response['username'], response['password'])
        self.client.run(['credential', 'approve'], self.repo_path, self.on_credentials_approved, stdin=request, config=config)

    def on_credentials_approved(self, exit_code, stdout, stderr):
        operation = self.remote_operation
        self.client.run(operation['arguments'], self.repo_path, self.on_remote_operation_finished, config=operation['config'])

    def reject_credentials(self):
        ''' Don't let a credential that just failed stay in a helper. '''

        if self.remote_operation['config'] == None: return

        request = git_client.format_credential_request(self.credential_description, self.credential_description.get('username'), self.credential_password)
        self.client.run(['credential', 'reject'], self.repo_path, None, stdin=request, config=self.remote_operation['config'])
        self.credential_password = None
