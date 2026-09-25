from app.utils import available_locales, load_data


def test_load_data():
    # it should load data from json.
    data = load_data()
    assert isinstance(data, tuple)
    assert len(data) > 0


def test_load_data_locale():
    # it should load data for a specific locale.
    english = load_data("en")
    italian = load_data("it")
    assert len(english) > 0
    assert len(italian) > 0
    assert english != italian


def test_available_locales():
    # it should discover locales from db/data.<locale>.json files.
    locales = available_locales()
    assert isinstance(locales, tuple)
    assert "en" in locales
    assert "it" in locales
    assert locales == tuple(sorted(locales))
