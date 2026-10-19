# -*- coding: utf-8 -*-

"""
Run one cdk action on one stack, or on every stack, of the current environment.

This is what every generated ``cdk-<action>-<env>-<stack>-stack`` and
``cdk-<action>-<env>-all`` mise task runs,
through ``cdk/cdk_cmd.py``; the task sets ``ENV_NAME`` for its process::

    ENV_NAME=dev .venv/bin/python cdk/cdk_cmd.py up alerts   # mise run cdk-up-dev-alerts-stack
    ENV_NAME=prd .venv/bin/python cdk/cdk_cmd.py plan all    # mise run cdk-plan-prd-all

It builds the cdk command with cdk_mate from the stack contexts of
:mod:`~cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum`, then runs it in ``cdk/``
with ``one.bsm`` (the profile ``AWS_PROFILE_<ENV>``), without touching the
caller's ``os.environ``. The command line is logged before it runs. The cdk CLI
inherits ``ENV_NAME`` and passes it to the cdk app, which therefore creates the
stacks of the same environment.

- One stack runs with ``--exclusively``: exactly that stack, no dependency.
- ``all`` runs every stack in one command; the cdk CLI orders them by their dependencies.
"""

from __future__ import annotations

import typing as T
import argparse
import dataclasses

import cdk_mate.api as cdk_mate

from .stack_ctx_enum import StackCtxEnum
from .stack_ctx_enum import list_entry_names

if T.TYPE_CHECKING:  # pragma: no cover
    from cdk_mate.api import StackCtx
    from ..one.api import One

ALL = "all"
"""
The reserved stack name that targets every stack; no stack may use it.
"""


@dataclasses.dataclass(frozen=True)
class CdkAction:
    """
    One kind of ``cdk-<name>-<env>-<stack>-stack`` task.
    """

    # fmt: off
    name: str = dataclasses.field()  #: The action part of the task name, such as ``up``.
    emoji: str = dataclasses.field()  #: Shown in front of the task description.
    summary: str = dataclasses.field()  #: The task description, with ``{target}`` and ``{env}`` placeholders.
    cmd_class: type[cdk_mate.cli.BaseCommand] = dataclasses.field()  #: The cdk_mate command, such as ``Deploy``.
    use_bsm: bool = dataclasses.field()  #: Whether it needs AWS credentials; ``synth`` does not.
    kwargs: dict[str, T.Any] = dataclasses.field(default_factory=dict)  #: Extra fields of the command.
    # fmt: on


CDK_ACTIONS: list[CdkAction] = [
    # fmt: off
    CdkAction(
        name="synth",
        emoji="⚪",
        summary="Synthesize {target} of {env} to CloudFormation templates (no AWS call)",
        cmd_class=cdk_mate.cli.Synth,
        use_bsm=False,
    ),
    CdkAction(
        name="plan",
        emoji="🔵",
        summary="Plan {target} of {env}: diff against what is deployed, through a CloudFormation change set (no deploy)",
        cmd_class=cdk_mate.cli.Diff,
        use_bsm=True,
        kwargs={"method": "auto"},
    ),
    CdkAction(
        name="up",
        emoji="🟢",
        summary="Deploy {target} of {env} (no approval prompt)",
        cmd_class=cdk_mate.cli.Deploy,
        use_bsm=True,
    ),
    CdkAction(
        name="down",
        emoji="🔴",
        summary="Destroy {target} of {env} (force, no confirmation)",
        cmd_class=cdk_mate.cli.Destroy,
        use_bsm=True,
    ),
    # fmt: on
]
"""
The four actions every (environment, stack) gets, in the order they appear in ``mise.toml``.
"""

CDK_ACTION_MAP: dict[str, CdkAction] = {action.name: action for action in CDK_ACTIONS}
"""
:data:`CDK_ACTIONS` by name.
"""


def to_stack_slug(stack: str) -> str:
    """
    The stack part of a task name, such as ``my-stack`` for the entry stack ``my_stack``.
    """
    return stack.replace("_", "-")


def get_stack_ctx_list(
    stack_ctx_enum: StackCtxEnum,
    stack: str,
) -> list[StackCtx]:
    """
    The stack contexts a command targets.

    :param stack: a stack slug, such as ``alerts``, or :data:`ALL`.
    """
    if stack == ALL:
        return stack_ctx_enum.get_all()
    return [stack_ctx_enum.get(stack.replace("-", "_"))]


def build_cdk_cmd(
    action: CdkAction,
    stack: str,
    stack_ctx_list: list[StackCtx],
) -> cdk_mate.cli.BaseCommand:
    """
    Build the cdk command, without running it; ``.to_args()`` shows its command line.
    """
    kwargs = dict(action.kwargs)
    if stack != ALL:
        kwargs["exclusively"] = True
    return cdk_mate.build_cmd(
        action.cmd_class,
        stack_ctx_list,
        prompt=False,
        **kwargs,
    )


def run_cdk_cmd(
    one: One,
    action_name: str,
    stack: str,
    dir_cdk,
):  # pragma: no cover
    """
    Build and run the cdk command in ``dir_cdk``, for the current environment,
    with ``one.bsm`` unless the action needs no AWS credentials.
    """
    action = CDK_ACTION_MAP[action_name]
    print(f"--- Environment: {one.env.current_env_name} ---")
    stack_ctx_list = get_stack_ctx_list(one.stack_ctx_enum, stack)
    cmd = build_cdk_cmd(action, stack, stack_ctx_list)
    for stack_ctx in stack_ctx_list:
        print(f"{stack_ctx.stack_name}: {stack_ctx.stack_console_url}")
    bsm = stack_ctx_list[0].bsm if action.use_bsm else None
    return cmd.run(bsm=bsm, dir_cdk=dir_cdk)


def make_parser() -> argparse.ArgumentParser:
    """
    The command line of ``cdk/cdk_cmd.py``: ``<action> <stack>``.
    """
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("action", choices=list(CDK_ACTION_MAP))
    stacks = [to_stack_slug(name) for name in list_entry_names(StackCtxEnum)]
    parser.add_argument("stack", choices=[ALL, *stacks])
    return parser
