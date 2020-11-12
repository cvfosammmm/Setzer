# Validate metainfo file
appstreamcli = find_program(
  'appstreamcli',
  required: false,
)
if appstreamcli.found()
  test(
    'validate metainfo file',
    appstreamcli,
    args: ['validate', '--no-net', '--pedantic', metainfo_file],
  )
endif

# Validate .desktop file
desktop_file_validate =  find_program(
  'desktop-file-validate',
  required: false,
)
if desktop_file_validate.found()
  test(
    'validate .desktop file',
    desktop_file_validate,
    args: [desktop_file]
  )
endif
