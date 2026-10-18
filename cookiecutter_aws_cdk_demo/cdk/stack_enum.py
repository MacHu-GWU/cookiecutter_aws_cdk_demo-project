# -*- coding: utf-8 -*-

"""
The registry of every CDK stack in this project.
"""

from __future__ import annotations

import dataclasses
from functools import cached_property

import aws_cdk as cdk

from ..config.api import Config
from ..one.api import One
from ..one.api import one
from .stacks.param_stack import ParamStack


@dataclasses.dataclass
class StackEnum:
    """
    Every stack of the app, one ``@cached_property`` each, built on first access.

    This class is the single source of truth for the stack list: ``cdk_app.py``
    synthesizes :attr:`stacks`, and ``mise run cdk-gen-tasks`` turns their short
    names into the ``cdk-*-<short_name>`` tasks. To add a stack:

    1. Add ``stack_short_name_<x>`` to ``Config``, and ``cft_stack_name_<x>`` /
       ``cft_stack_url_<x>`` to ``ConfigNameMixin``.
    2. Write the stack class under ``stacks/``, taking ``(scope, id, config, **kwargs)``.
    3. Add a ``@cached_property`` here that builds it with ``id=self.config.cft_stack_name_<x>``,
       ``config=self.config``, and ``env=self.cdk_env``.
    4. Run ``mise run cdk-gen-tasks``.
    """

    # fmt: off
    app: cdk.App = dataclasses.field()  #: The CDK app that owns every stack.
    one: One = dataclasses.field()  #: The project singleton; stacks get only its ``config``.
    # fmt: on

    @cached_property
    def config(self) -> Config:
        """
        The config of the environment being deployed, ``one.config``.
        """
        return self.one.config

    @cached_property
    def cdk_env(self) -> cdk.Environment:
        """
        The account and region from the config. Every stack is bound to it, so the
        cdk CLI also refuses to deploy with credentials of another account.
        """
        return cdk.Environment(
            account=self.config.aws_account_id,
            region=self.config.aws_region,
        )

    @cached_property
    def param_stack(self) -> ParamStack:
        """
        The sample stack with one SSM parameter.
        """
        return ParamStack(
            scope=self.app,
            id=self.config.cft_stack_name_param,
            config=self.config,
            env=self.cdk_env,
        )

    @property
    def stacks(self) -> list[cdk.Stack]:
        """
        Every stack, in the order the properties are defined in this class.

        Any ``@cached_property`` of this class that returns an ``aws_cdk.Stack``
        counts, so a new stack needs no second registration here.
        """
        stacks = []
        for name, attr in type(self).__dict__.items():
            if isinstance(attr, cached_property):
                value = getattr(self, name)
                if isinstance(value, cdk.Stack):
                    stacks.append(value)
        return stacks

    @property
    def stack_short_names(self) -> list[str]:
        """
        The short name of every stack: its name without ``config.prefix_name_slug``.

        :raises ValueError: a stack name does not start with ``<prefix_name_slug>-``.
        """
        prefix = f"{self.config.prefix_name_slug}-"
        short_names = []
        for stack in self.stacks:
            if not stack.stack_name.startswith(prefix):
                raise ValueError(
                    f"stack name {stack.stack_name!r} must start with {prefix!r}, "
                    "build it with config.get_cft_stack_name()"
                )
            short_names.append(stack.stack_name[len(prefix) :])
        return short_names

    def synth(self) -> None:
        """
        Build every stack, then synthesize the app into ``cdk.out``.
        """
        _ = self.stacks
        self.app.synth()


stack_enum = StackEnum(
    app=cdk.App(),
    one=one,
)
"""
The stack registry of this project; ``cdk/cdk_app.py`` synthesizes it.
"""
