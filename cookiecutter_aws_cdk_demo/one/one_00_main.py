# -*- coding: utf-8 -*-

"""
The ``One`` class: a single entry point to every project-level singleton.

Instead of importing ``env``, ``runtime``, the config, and the boto session from
four places, code imports ``one`` and reads ``one.env``, ``one.runtime``,
``one.config``, ``one.boto_ses``, and so on.

**Why mixins:** each concern lives in its own numbered module (``one_01_config.py``,
``one_02_boto_ses.py``, ...), so a reader looking for "how is the boto session
built?" opens one short file. The number gives the dependency order: config comes
before the session, the session before anything that calls AWS. All mixins share
``self``, so a property in one mixin reads another's (``self.config``,
``self.boto_ses``) without any wiring.

**To add a concern:** create ``one_0N_xxx.py`` with a ``OneXxxMixin`` class whose
properties are ``@cached_property``, then add the mixin to the bases of :class:`One`.

Every property is computed on first access, so importing ``one`` does no work and
makes no AWS call.
"""

from __future__ import annotations

from ..env import env
from ..runtime import runtime
from .one_01_config import OneConfigMixin
from .one_02_boto_ses import OneBotoSesMixin


class One(
    OneConfigMixin,
    OneBotoSesMixin,
):
    """
    Aggregates every project-level singleton. Use the module-level :data:`~cookiecutter_aws_cdk_demo.one.one_00_main.one`.
    """

    # fmt: off
    env = env  #: The deployment environment detector, see :mod:`cookiecutter_aws_cdk_demo.env`.
    runtime = runtime #: The runtime detector, see :mod:`cookiecutter_aws_cdk_demo.runtime`.
    # fmt: on


one = One()
"""
The single :class:`One` instance of this project.
"""
