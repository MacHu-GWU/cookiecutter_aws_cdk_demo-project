# -*- coding: utf-8 -*-

"""
Layer 1 of the cdk_mate two-layer pattern: one stack context per stack.

A :class:`~cdk_mate.stack_ctx.StackCtx` is plain data that names one stack
(construct ID, stack name, account, region) plus the boto session that deploys it.
Every entry belongs to the current environment: its names, account, and region
come from ``one.config``, and its session is ``one.bsm``. Building one creates no
CDK construct and makes no AWS call.

- **Who uses it:** :mod:`~cookiecutter_aws_cdk_demo.cdk.cdk_cmd`, which the
  ``cdk-*`` mise tasks run. Deploying needs the stack names and the credentials,
  not the stack objects; the cdk CLI builds the stacks itself by running the app.
- **Layer 2,** :mod:`~cookiecutter_aws_cdk_demo.cdk.stack_enum`, creates the CDK
  stack of each entry, with an attribute of the same name.
- **Naming:** the attribute name is the stack name, such as ``alerts``; with ``_``
  turned into ``-``, it is also the stack part of the mise task names. Entries are
  listed in creation order: a stack comes after the stacks it depends on.

Use it as ``one.stack_ctx_enum``. To add a stack, add one entry here and one in
:class:`~cookiecutter_aws_cdk_demo.cdk.stack_enum.StackEnum`, then run
``mise run cdk-gen-tasks``.
"""

from __future__ import annotations

import typing as T
import dataclasses
from functools import cached_property

from cdk_mate.api import StackCtx
from cdk_mate.api import to_camel
from cdk_mate.api import to_slug

if T.TYPE_CHECKING:  # pragma: no cover
    from ..one.api import One


def list_entry_names(klass: type) -> list[str]:
    """
    The names of the cached properties of ``klass``, in definition order.
    Reads only the class, so it builds nothing.
    """
    return [
        name
        for name, attr in klass.__dict__.items()
        if isinstance(attr, cached_property)
    ]


@dataclasses.dataclass
class StackCtxEnum:
    """
    One :class:`~cdk_mate.stack_ctx.StackCtx` per stack of the current
    environment, built on first access.
    """

    # fmt: off
    one: One = dataclasses.field()  #: The project singleton, for ``config`` and ``bsm``.
    # fmt: on

    def _new(self, stack_name: str) -> StackCtx:
        """
        The context of ``stack_name``. The construct ID is the stack name in
        CamelCase, as in :meth:`cdk_mate.stack_ctx.StackCtx.new`, but the account
        and region come from the config instead of an STS call.
        """
        return StackCtx(
            construct_id=to_camel(stack_name),
            stack_name=to_slug(stack_name),
            aws_account_id=self.one.config.aws_account_id,
            aws_region=self.one.config.aws_region,
            bsm=self.one.bsm,
        )

    @cached_property
    def alerts(self) -> StackCtx:
        return self._new(self.one.config.cft_stack_name_alerts)

    @cached_property
    def publisher(self) -> StackCtx:
        """
        Depends on :attr:`alerts`.
        """
        return self._new(self.one.config.cft_stack_name_publisher)

    def get(self, stack: str) -> StackCtx:
        """
        The entry of one stack given by name, such as ``get("alerts")``.

        :raises AttributeError: there is no such entry.
        """
        return getattr(self, stack)

    def get_all(self) -> list[StackCtx]:
        """
        Every entry, in creation order.
        """
        return [getattr(self, name) for name in list_entry_names(type(self))]
