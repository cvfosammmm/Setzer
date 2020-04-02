project(
  'Setzer',
  version: '0.2.2',
  license: 'GPLv3',
)

# runtime dependencies
dependency('gtk+-3.0')
dependency('gtksourceview-3.0')
dependency('poppler-glib')
dependency('gspell-1')

# python configuration
python_modules = [
  'gi',
]
if meson.version().version_compare('>=0.51')
  py = import('python').find_installation(modules: python_modules)
else
  py = import('python').find_installation()
  foreach module: python_modules
    if run_command(py, '-c', 'import @0@'.format(module)).returncode() != 0
      error('Failed to find required python module "@0@".'.format(module))
    endif
  endforeach
endif

# configure folders
prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
pymdir = py.get_install_dir()
resourcesdir = join_paths(datadir, 'Setzer')

config = configuration_data()
config.set('resources_path', join_paths(prefix, resourcesdir, 'resources'))
config.set('app_icons_path', join_paths(prefix, datadir, 'icons'))

config_dev = config
config_dev.set('resources_path', join_paths(meson.source_root(), 'data', 'resources'))
config_dev.set('app_icons_path', join_paths(meson.source_root(), 'data'))

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
