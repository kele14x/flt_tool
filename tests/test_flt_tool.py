import flt_tool


def test_self_recursive():
    flt_tool.main(['self_recursive.flt', '-p'])


def test_cycle_ref():
    flt_tool.main(['cycle_ref_a.flt', '-p'])
