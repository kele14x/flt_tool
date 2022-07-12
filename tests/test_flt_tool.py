import flt_tool


def test_version():
    try:
        flt_tool.main(['--version'])
    except SystemExit as e:
        assert e.code == 0


def test_help():
    try:
        flt_tool.main(['--help'])
    except SystemExit as e:
        assert e.code == 0


def test_self_recursive():
    try:
        flt_tool.main(['self_recursive.flt', '-p'])
    except SystemExit as e:
        assert e.code == 0


def test_cycle_ref():
    try:
        flt_tool.main(['cycle_ref_a.flt', '-p'])
    except SystemExit as e:
        assert e.code == 0
