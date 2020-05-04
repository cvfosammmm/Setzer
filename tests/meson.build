# Validate MetaInfo file
appstreamcli = find_program(
  'appstreamcli',
  required: false
)
if appstreamcli.found()
  test(
    'validate metainfo file',
    appstreamcli,
    args: ['validate', '--no-net', '--pedantic', metainfo_file],
  )
endif
