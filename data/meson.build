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

install_man(
  files('setzer.1'),
  install_dir: join_paths(mandir, 'man1'),
)
