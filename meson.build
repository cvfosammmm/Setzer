project(
  'Setzer',
  version: '0.2.0',
  license: 'GPLv3',
  meson_version: '>=0.51',
)

# runtime dependencies
dependency('gtk+-3.0')
dependency('gtksourceview-3.0')
dependency('poppler-glib')
dependency('gspell-1')

# python configuration
python_modules = ['gi']
py = import('python').find_installation(modules: python_modules)

# configure folders
bindir = get_option('bindir')
datadir = get_option('datadir')
pymdir = py.get_install_dir()

# install python sources
install_subdir(
  'setzer',
  install_dir: pymdir,
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
  input: '__main__.py',
  output: 'setzer',
  copy: true,
  install_dir: bindir,
)
