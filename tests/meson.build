# Validate MetaInfo file
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

# Test PEP 8 conformance
flake8 = find_program(
  'flake8',
  required: false,
)
if flake8.found()
  test(
    'test PEP 8 conformance',
    flake8,
    args: ['--builtins=_'],
  )
endif
