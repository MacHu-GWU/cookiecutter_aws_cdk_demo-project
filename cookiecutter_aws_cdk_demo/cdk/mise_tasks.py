# -*- coding: utf-8 -*-

"""
Generate the ``cdk-*`` mise tasks: one per (action, environment, stack).

Each (environment, stack) pair gets four tasks named ``cdk-<action>-<env>-<stack>-stack``,
such as ``cdk-up-dev-alerts-stack``; the ``-stack`` ending marks a task that acts on
one stack only. ``cdk-<action>-<env>-all`` runs the action on every stack, so no
stack may be named ``all``.

Each task is one plain cdk command, run in ``cdk/``:

- ``ENV_NAME=<env>`` is set for the task, and the cdk CLI passes it to the cdk app,
  which then creates the stacks of that environment only.
- ``--profile {{env.AWS_PROFILE_FOR_<ENV>}}`` gives the cdk CLI the credentials of
  that environment; mise reads the value from ``.env`` and stops with an error if
  it is not set. ``synth`` makes no AWS call, so it takes no profile.
- One stack is selected by its construct ID, which is its stack name, with
  ``--exclusively``; ``all`` uses ``--all`` and lets the cdk CLI order the stacks
  by their dependencies.

The stacks come from the entry names of
:class:`~cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum.StackCtxEnum`, the environments
from :class:`~cookiecutter_aws_cdk_demo.env.EnvNameEnum`, and the construct IDs from
the config of each environment; nothing calls AWS.
The tasks live in ``mise.toml`` between :data:`BEGIN_MARKER` and :data:`END_MARKER`;
``mise run cdk-gen-tasks`` rewrites that block and leaves the rest of the file alone.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from ..env import ENV_NAME_VAR
from ..env import EnvNameEnum
from ..runtime import RuntimeNameEnum
from ..config.api import Config
from ..one.api import One
from ..one.one_02_boto_ses import get_aws_profile_env_var
from .stack_ctx_enum import StackCtxEnum
from .stack_ctx_enum import list_entry_names

ALL = "all"
"""
The reserved stack name that targets every stack; no stack may use it.
"""

BEGIN_MARKER = "# <cdk-stack-tasks>"
"""
The line that opens the generated block in ``mise.toml``.
"""

END_MARKER = "# </cdk-stack-tasks>"
"""
The line that closes the generated block in ``mise.toml``.
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
    command: str = dataclasses.field()  #: The cdk command with its options, such as ``deploy --require-approval never``.
    use_profile: bool = dataclasses.field()  #: Whether it calls AWS and needs ``--profile``; ``synth`` does not.
    # fmt: on


CDK_ACTIONS: list[CdkAction] = [
    # fmt: off
    CdkAction(
        name="synth",
        emoji="⚪",
        summary="Synthesize {target} of {env} to CloudFormation templates (no AWS call)",
        command="synth",
        use_profile=False,
    ),
    CdkAction(
        name="plan",
        emoji="🔵",
        summary="Plan {target} of {env}: diff against what is deployed, through a CloudFormation change set (no deploy)",
        command="diff --method auto",
        use_profile=True,
    ),
    CdkAction(
        name="up",
        emoji="🟢",
        summary="Deploy {target} of {env} (no approval prompt)",
        command="deploy --require-approval never",
        use_profile=True,
    ),
    CdkAction(
        name="down",
        emoji="🔴",
        summary="Destroy {target} of {env} (force, no confirmation)",
        command="destroy --force",
        use_profile=True,
    ),
    # fmt: on
]
"""
The four actions every (environment, stack) gets, in the order they appear in ``mise.toml``.
"""


def to_stack_slug(stack: str) -> str:
    """
    The stack part of a task name, such as ``my-stack`` for the entry ``my_stack``.
    """
    return stack.replace("_", "-")


def validate_stacks(stacks: list[str]) -> None:
    """
    Check that the stack names can be used in task names.

    :raises ValueError: a stack is named :data:`ALL`, or two stacks share a slug.
    """
    slugs = [to_stack_slug(stack) for stack in stacks]
    if ALL in slugs:
        raise ValueError(
            f"stack name {ALL!r} is reserved for the cdk-*-{ALL} tasks, rename the stack"
        )
    if len(set(slugs)) != len(slugs):
        raise ValueError(f"duplicate stack name in {stacks}")


def get_construct_ids(env_name: str) -> dict[str, str]:
    """
    The construct ID of every stack of one environment, by entry name, in creation
    order, such as ``{"alerts": "my-project-dev-alerts", ...}``. It loads the
    config of that environment; it makes no AWS call.
    """
    one = One()
    one.config = Config.load(
        env_name=env_name,
        runtime_name=RuntimeNameEnum.local.value,
    )
    stack_ctx_enum = StackCtxEnum(one=one)
    return {
        stack: stack_ctx_enum.get(stack).construct_id
        for stack in list_entry_names(StackCtxEnum)
    }


def get_task_name(
    action_name: str,
    env_name: str,
    stack_slug: str,
) -> str:
    """
    The name of a generated task: ``cdk-<action>-<env>-all`` for every stack,
    ``cdk-<action>-<env>-<stack>-stack`` for one, such as ``cdk-up-dev-alerts-stack``.
    """
    if stack_slug == ALL:
        return f"cdk-{action_name}-{env_name}-{ALL}"
    return f"cdk-{action_name}-{env_name}-{stack_slug}-stack"


def get_cdk_command(
    action: CdkAction,
    env_name: str,
    construct_id: str | None,
) -> str:
    """
    The cdk command line of a task, such as
    ``cdk deploy my-project-dev-alerts --exclusively --require-approval never --profile {{env.AWS_PROFILE_FOR_DEV}}``.

    :param construct_id: the stack to act on, or ``None`` for every stack (``--all``).
    """
    sub_command, _, options = action.command.partition(" ")
    parts = ["cdk", sub_command]
    if construct_id is None:
        parts.append("--all")
    else:
        parts.extend([construct_id, "--exclusively"])
    if options:
        parts.append(options)
    if action.use_profile:
        parts.append(f"--profile {{{{env.{get_aws_profile_env_var(env_name)}}}}}")
    return " ".join(parts)


def _render_task(
    action: CdkAction,
    env_name: str,
    stack_slug: str,
    construct_id: str | None,
) -> str:
    target = "all stacks" if construct_id is None else f"stack {stack_slug}"
    summary = action.summary.format(target=target, env=env_name)
    task_name = get_task_name(action.name, env_name, stack_slug)
    command = get_cdk_command(action, env_name, construct_id)
    lines = [
        f'[tasks."{task_name}"]',
        f'description = "{action.emoji} {summary}"',
        'dir = "cdk"',
        f'env = {{ {ENV_NAME_VAR} = "{env_name}" }}',
        'depends = ["inst"]',
        f'run = "{command}"',
    ]
    return "\n".join(lines)


def render_cdk_tasks(env_construct_ids: dict[str, dict[str, str]]) -> str:
    """
    Render the whole generated block, markers included.

    :param env_construct_ids: for each environment, the construct ID of each stack
        by entry name, see :func:`get_construct_ids`. Tasks follow its order: by
        environment, then the ``all`` tasks, then each stack.

    :raises ValueError: see :func:`validate_stacks`.
    """
    header = (
        f"{BEGIN_MARKER}\n"
        "# Generated by ``mise run cdk-gen-tasks`` from StackCtxEnum. Do not edit by hand."
    )
    parts = [header]
    for env_name, construct_ids in env_construct_ids.items():
        validate_stacks(list(construct_ids))
        targets = [(ALL, None)]
        for stack, construct_id in construct_ids.items():
            targets.append((to_stack_slug(stack), construct_id))
        for stack_slug, construct_id in targets:
            for action in CDK_ACTIONS:
                task = _render_task(
                    action=action,
                    env_name=env_name,
                    stack_slug=stack_slug,
                    construct_id=construct_id,
                )
                parts.append(task)
    parts.append(END_MARKER)
    return "\n\n".join(parts)


def render_project_cdk_tasks() -> str:
    """
    :func:`render_cdk_tasks` for every stack of this project in every environment.
    """
    env_construct_ids = {
        member.value: get_construct_ids(member.value) for member in EnvNameEnum
    }
    return render_cdk_tasks(env_construct_ids)


def replace_cdk_tasks_block(text: str, block: str) -> str:
    """
    Replace the generated block in the ``mise.toml`` text, markers included.

    :param text: the content of ``mise.toml``.
    :param block: the new block, from :func:`render_cdk_tasks`.

    :raises ValueError: the markers are missing, or the end marker comes first.
    """
    begin = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)
    if begin == -1 or end == -1 or end < begin:
        raise ValueError(
            f"mise.toml must contain the lines {BEGIN_MARKER!r} and {END_MARKER!r}, in this order"
        )
    end = end + len(END_MARKER)
    return text[:begin] + block + text[end:]


def update_mise_toml(
    path: Path,
    block: str,
) -> bool:
    """
    Rewrite the generated block of the ``mise.toml`` at ``path``.

    :param block: the new block, such as :func:`render_project_cdk_tasks`.

    :returns: ``True`` if the file changed, ``False`` if it was already up to date.
    """
    text = path.read_text(encoding="utf-8")
    new_text = replace_cdk_tasks_block(text, block)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True
