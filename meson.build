project(
  'Setzer',
  version: '66',
  license: 'GPL-3.0-or-later',
)

python = import('python').find_installation()
python_bin = python.full_path()

# configure folders
prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
pymdir = python.get_install_dir()
resourcesdir = join_paths(datadir, 'Setzer')
localedir = get_option('localedir')
mandir = get_option('mandir')

config = configuration_data()
config.set('setzer_version', meson.project_version())
config.set('localedir_path', join_paths(prefix, localedir))
config.set('resources_path', join_paths(prefix, resourcesdir, 'resources'))
config.set('app_icons_path', join_paths(prefix, datadir, 'icons'))
config.set('python_path', python_bin)

config_dev = config
config_dev.set('localedir_path', '/tmp/usr/share/locale') # this is a workaround
config_dev.set('resources_path', join_paths(meson.source_root(), 'data', 'resources'))
config_dev.set('app_icons_path', join_paths(meson.source_root(), 'data'))

# install translations
subdir('po')

# install python sources
install_subdir(
  'setzer',
  install_dir: pymdir,
)

# install resources
install_subdir(
  join_paths('data', 'resources'),
  install_dir: resourcesdir,
)

# install program data
subdir('data')

# install binary
configure_file(
  input: 'setzer.in',
  output: 'setzer',
  configuration: config,
  install: true,
  install_dir: bindir,
)

# create devel binary
configure_file(
  input: 'setzer.in',
  output: 'setzer_dev.py',
  configuration: config_dev,
)

# run tests
subdir('tests')
