"""Stand-ins for the MicroPython modules pico_nhl imports, so it can be tested under CPython.

pico_nhl imports `urequests` and `utime`, which only exist on MicroPython. Call
`install()` before importing pico_nhl; it registers fake versions of both in
`sys.modules`:

* `urequests.get(url)` records the URL and returns whatever response was queued
  with `serve()` / `serve_fixture()`.
* `utime.time()` returns the value set with `set_time()`.
* `utime.mktime()` accepts MicroPython's 8-tuple and treats it as UTC, which is
  how it behaves on a Pico whose RTC is set to UTC (e.g. via `ntptime`).
"""

import calendar
import json
import sys
import types
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FakeResponse:
    """Mimics the parts of a MicroPython requests Response that pico_nhl uses."""

    def __init__(self, status_code: int, content: bytes):
        self.status_code = status_code
        self.content = content

    def json(self):
        return json.loads(self.content)


class _State:
    response = None
    requested_urls = []
    now = 0


def _get(url, *args, **kwargs):
    _State.requested_urls.append(url)
    if _State.response is None:
        raise AssertionError(f"unexpected request (no response queued): {url}")
    return _State.response


def _mktime(time_tuple):
    if len(time_tuple) != 8:
        raise TypeError("MicroPython's mktime takes an 8-tuple")
    return calendar.timegm(tuple(time_tuple[:6]) + (0, 0, 0))


def install():
    """Register the fake `urequests` and `utime` modules (idempotent)."""
    urequests = types.ModuleType("urequests")
    urequests.get = _get
    utime = types.ModuleType("utime")
    utime.time = lambda: _State.now
    utime.mktime = _mktime
    sys.modules.setdefault("urequests", urequests)
    sys.modules.setdefault("utime", utime)


def reset():
    _State.response = None
    _State.requested_urls = []
    _State.now = 0


def serve(status_code: int, content: bytes):
    """Queue the response every subsequent `urequests.get` call returns."""
    _State.response = FakeResponse(status_code, content)


def load_fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def serve_fixture(name: str, status_code: int = 200):
    serve(status_code, load_fixture(name))


def requested_urls():
    return list(_State.requested_urls)


def set_time(iso_utc: str):
    """Set utime.time() from an ISO-8601 UTC timestamp like '2026-10-31T22:46:32Z'."""
    _State.now = epoch(iso_utc)


def epoch(iso_utc: str) -> int:
    date_part, time_part = iso_utc.rstrip("Z").split("T")
    year, month, day = map(int, date_part.split("-"))
    hour, minute, second = map(int, time_part.split(".")[0].split(":"))
    return calendar.timegm((year, month, day, hour, minute, second, 0, 0, 0))
