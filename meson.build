project(
  'Setzer',
  version: '0.2.5',
  license: 'GPL-3.0-or-later',
)

# configure folders
prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
pymdir = import('python').find_installation().get_install_dir()
resourcesdir = join_paths(datadir, 'Setzer')
localedir = get_option('localedir')

config = configuration_data()
config.set('setzer_version', meson.project_version())
config.set('localedir_path', join_paths(prefix, localedir))
config.set('resources_path', join_paths(prefix, resourcesdir, 'resources'))
config.set('app_icons_path', join_paths(prefix, datadir, 'icons'))

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
install_data(
  join_paths('data', 'org.cvfosammmm.Setzer.desktop'),
  install_dir: join_paths(datadir, 'applications'),
)

install_data(
  join_paths('data', 'org.cvfosammmm.Setzer.svg'),
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
)

install_data(
  join_paths('data', 'org.cvfosammmm.Setzer.appdata.xml'),
  install_dir: join_paths(datadir, 'metainfo'),
)

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
