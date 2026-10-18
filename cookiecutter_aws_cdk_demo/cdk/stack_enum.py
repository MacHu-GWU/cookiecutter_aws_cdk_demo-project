# -*- coding: utf-8 -*-

"""
The registry of every CDK stack in this project.
"""

from __future__ import annotations

import dataclasses
from functools import cached_property

import aws_cdk as cdk

from ..one.api import One
from ..one.api import one
from .stacks.param_stack import ParamStack


@dataclasses.dataclass
class StackEnum:
    """
    Every stack of the app, one ``@cached_property`` each, built on first access.

    This class is the single source of truth for the stack list: ``cdk_app.py``
    synthesizes :attr:`stacks`, and ``mise run cdk-gen-tasks`` turns their IDs into
    the ``cdk-*-<slug>`` tasks. To add a stack, write its class under ``stacks/``,
    add a ``@cached_property`` here that returns it, then run ``mise run cdk-gen-tasks``.
    """

    # fmt: off
    app: cdk.App = dataclasses.field()  #: The CDK app that owns every stack.
    one: One = dataclasses.field()  #: The project singleton passed to every stack.
    # fmt: on

    @cached_property
    def param_stack(self) -> ParamStack:
        """
        The sample stack with one SSM parameter.
        """
        return ParamStack(
            scope=self.app,
            id=self.one.config.get_stack_id("param"),
            one=self.one,
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
