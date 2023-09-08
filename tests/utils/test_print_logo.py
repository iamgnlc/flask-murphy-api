from app.utils import print_logo


def test_print_logo(capfd):
    # it should print an output.
    print_logo()
    out, err = capfd.readouterr()
    assert len(out) > 10  # 10 is the length of the output witout a logo.
