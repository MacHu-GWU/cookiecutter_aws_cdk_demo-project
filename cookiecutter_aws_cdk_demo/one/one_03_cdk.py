# -*- coding: utf-8 -*-

"""
The CDK part of ``one``: the two layers of the cdk_mate pattern,
:attr:`~cookiecutter_aws_cdk_demo.one.one_03_cdk.OneCdkMixin.stack_ctx_enum` and
:attr:`~cookiecutter_aws_cdk_demo.one.one_03_cdk.OneCdkMixin.stack_enum`.

The CDK modules are imported inside the properties, so importing ``one`` does not
load ``aws_cdk`` (which starts a node process); only the code that uses them pays.
"""

from __future__ import annotations

import typing as T
from functools import cached_property

if T.TYPE_CHECKING:  # pragma: no cover
    from ..cdk.stack_ctx_enum import StackCtxEnum
    from ..cdk.stack_enum import StackEnum
    from .one_00_main import One


class OneCdkMixin:
    """
    Lazily built CDK stack contexts and stacks.
    """

    @cached_property
    def stack_ctx_enum(self: One) -> StackCtxEnum:
        """
        One ``cdk_mate.StackCtx`` per (stack, environment), such as
        ``one.stack_ctx_enum.alerts_dev``. See :mod:`cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum`.
        """
        from ..cdk.stack_ctx_enum import StackCtxEnum

        return StackCtxEnum(one=self)

    @cached_property
    def stack_enum(self: One) -> StackEnum:
        """
        One CDK stack per (stack, environment), in a new ``cdk.App``, such as
        ``one.stack_enum.alerts_dev``; ``cdk/cdk_app.py`` synthesizes it.
        See :mod:`cookiecutter_aws_cdk_demo.cdk.stack_enum`.
        """
        import aws_cdk as cdk

        from ..cdk.stack_enum import StackEnum

        return StackEnum(app=cdk.App(), one=self)
