install_data(
  files('org.cvfosammmm.Setzer.desktop'),
  install_dir: join_paths(datadir, 'applications'),
)

install_data(
  files('org.cvfosammmm.Setzer.svg'),
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
)

metainfo_file = i18n.merge_file(
  input:  files('org.cvfosammmm.Setzer.appdata.xml.in'),
  output: 'org.cvfosammmm.Setzer.appdata.xml',
  type: 'xml',
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(datadir, 'metainfo'),
)

config_man = configuration_data()
config_man.set('VERSION', meson.project_version())

man_file = configure_file(
  input: files('setzer.1.in'),
  output: 'setzer.1',
  configuration: config_man,
)

install_man(
  man_file,
  install_dir: join_paths(mandir, 'man1'),
)
