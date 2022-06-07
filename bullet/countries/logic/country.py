from threading import local

_country = local()


def get_country():
    try:
        return _country.value
    except AttributeError:
        return None


def activate(country):
    _country.value = country


def deactivate():
    try:
        del _country.value
    except AttributeError:
        pass
