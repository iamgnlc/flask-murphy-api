import json
import os

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "db",
)


def load_data(locale: str = "en"):
    """Load data from db/data.<locale>.json file."""
    data_path = os.path.join(DATA_DIR, f"data.{locale}.json")
    with open(data_path) as file:
        data = tuple(json.load(file))

    return data


def available_locales():
    """Locales derived from db/data.<locale>.json files, sorted alphabetically."""
    locales = []
    for name in os.listdir(DATA_DIR):
        if name.startswith("data.") and name.endswith(".json"):
            locale = name[len("data.") : -len(".json")]
            if locale:
                locales.append(locale)

    return tuple(sorted(locales))
