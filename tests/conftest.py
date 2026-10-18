# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(autouse=True)
def local_runtime(monkeypatch):
    """
    Run every test as the local runtime, the only one that can load the config,
    even on a CI runner (which sets ``CI``).
    """
    monkeypatch.delenv("CI", raising=False)
