# -*- coding: utf-8 -*-

"""
Deployment environment detection: which environment (dev, tst, prd) this project targets.

A single code base usually deploys the same stacks to several environments.
Instead of reading ``os.environ`` in every module, code asks the module-level
:data:`env` singleton, so the detection rule lives in one place::

    from .env import env

    if env.current_env_name == "prd":
        ...

The value is computed on first access and cached, so importing this module
has no side effect.
"""

from __future__ import annotations

import enum
from functools import cached_property


class EnvNameEnum(enum.Enum):
    """
    Every environment this project can be deployed to.
    """

    #: Development, where engineers deploy and test freely.
    dev = "dev"
    #: Test, a production-like environment for integration and acceptance tests.
    tst = "tst"
    #: Production, serving real users.
    prd = "prd"


class Env:
    """
    Detects the current deployment environment.

    Use the module-level :data:`env` singleton instead of creating new instances.
    """

    def get_current_env_name(self) -> EnvNameEnum:
        """
        Work out the current environment; :attr:`current_env_name` caches the result.

        This template always returns :attr:`EnvNameEnum.dev`. Change it to the rule
        your project needs, such as reading an ``ENV_NAME`` environment variable
        or the git branch name.
        """
        return EnvNameEnum.dev

    @cached_property
    def current_env_name(self) -> str:
        """
        The current environment name, such as ``"dev"``, computed once on first access.
        """
        return self.get_current_env_name().value


env = Env()
"""
The single :class:`Env` instance of this project.
"""
