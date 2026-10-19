# -*- coding: utf-8 -*-

"""
Layer 2 of the cdk_mate two-layer pattern: one CDK stack per stack.

Layer 1, :mod:`~cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum`, says *which* stacks
exist and where they go. This module says *how* each one is created: one
``@cached_property`` per entry, with the same name, written out by hand:

- **Arguments by name.** Each property passes its stack's arguments explicitly,
  so a new ``__init__`` argument breaks every property that does not pass it,
  instead of hiding behind ``**kwargs``.
- **Dependencies are attribute access.** ``publisher`` passes
  ``self.alerts.alert_topic``, so it creates ``alerts`` first, and CDK turns the
  reference into an export of the alerts stack and an import in the publisher stack.
- **One instance per stack.** A cached property is built once; creating the
  same construct ID twice in one ``cdk.App`` is an error.

The app holds the stacks of the current environment only, the one ``ENV_NAME``
selects; ``cdk_app.py`` calls :meth:`StackEnum.synth`.

Use it as ``one.stack_enum``; tests create ``StackEnum(app=cdk.App(), one=...)``.
"""

from __future__ import annotations

import typing as T
import dataclasses
from functools import cached_property

import aws_cdk as cdk

from .stack_ctx_enum import list_entry_names
from .stacks.alerts_stack import AlertsStack
from .stacks.publisher_stack.stack import PublisherStack

if T.TYPE_CHECKING:  # pragma: no cover
    from ..one.api import One


@dataclasses.dataclass
class StackEnum:
    """
    One CDK stack per stack of the current environment, created in :attr:`app`
    on first access, named like its entry in
    :class:`~cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum.StackCtxEnum`.
    """

    # fmt: off
    app: cdk.App = dataclasses.field()  #: The CDK app that owns every stack.
    one: One = dataclasses.field()  #: The project singleton, for ``config`` and ``stack_ctx_enum``.
    # fmt: on

    @cached_property
    def alerts(self) -> AlertsStack:
        return AlertsStack(
            scope=self.app,
            **self.one.stack_ctx_enum.alerts.to_stack_kwargs(),
            config=self.one.config,
        )

    @cached_property
    def publisher(self) -> PublisherStack:
        return PublisherStack(
            scope=self.app,
            **self.one.stack_ctx_enum.publisher.to_stack_kwargs(),
            config=self.one.config,
            alert_topic=self.alerts.alert_topic,
        )

    def get_all(self) -> list[cdk.Stack]:
        """
        Create every stack, in creation order, and return them.
        """
        return [getattr(self, name) for name in list_entry_names(type(self))]

    def synth(self) -> None:
        """
        Create every stack, then synthesize the app into ``cdk.out``.
        """
        self.get_all()
        self.app.synth()
