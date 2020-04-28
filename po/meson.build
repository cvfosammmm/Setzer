i18n = import('i18n')

i18n.merge_file(
    input:  join_paths(meson.source_root(), 'data', 'org.cvfosammmm.Setzer.appdata.xml.in'),
    output: 'org.cvfosammmm.Setzer.appdata.xml',
    type: 'xml',
    po_dir: join_paths(meson.source_root(), 'po'),
    install: true,
    install_dir: join_paths(datadir, 'metainfo'),
)

i18n.gettext(
  'setzer',
  install_dir: localedir,
)
