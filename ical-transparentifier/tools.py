from urllib.parse import urlparse

import requests
from ics import Calendar
from requests.adapters import HTTPAdapter

webcal_adapter = HTTPAdapter()
rsession = requests.session()
rsession.mount('webcal://', webcal_adapter)


def _standardize_uri(uri: str) -> str:
    parsed = urlparse(uri)
    if parsed.scheme == "webcal":
        parsed = parsed._replace(scheme="https")
    return parsed.geturl()


def futz_with_ical(uri: str) -> str:
    cal_uri = _standardize_uri(uri)
    original_cal = rsession.get(cal_uri).text

    c = Calendar(original_cal)

    for event in c.events:
        event.transparent = True
    return str(c)