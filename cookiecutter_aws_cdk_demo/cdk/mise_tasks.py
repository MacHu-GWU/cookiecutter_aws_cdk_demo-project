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
- Before the cdk command, the task prints the CloudFormation console URL of each
  stack it acts on: one for a ``-stack`` task, all of them for an ``all`` task.

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
    all_option: str = dataclasses.field(default="--all")  #: Selects every stack; ``cdk synth`` has no ``--all`` and does every stack without one.
    # fmt: on


CDK_ACTIONS: list[CdkAction] = [
    # fmt: off
    CdkAction(
        name="synth",
        emoji="⚪",
        summary="Synthesize {target} of {env} to CloudFormation templates (no AWS call)",
        command="synth",
        use_profile=False,
        all_option="",
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


@dataclasses.dataclass(frozen=True)
class StackTarget:
    """
    What a task needs to know about one stack of one environment.
    """

    # fmt: off
    construct_id: str = dataclasses.field()  #: Selects the stack in the cdk CLI; it is the stack name.
    console_url: str = dataclasses.field()  #: The CloudFormation console URL, printed before the cdk command.
    # fmt: on


def get_stack_targets(env_name: str) -> dict[str, StackTarget]:
    """
    Every stack of one environment, by entry name, in creation order, such as
    ``{"alerts": StackTarget("my-project-dev-alerts", "https://..."), ...}``.
    It loads the config of that environment; it makes no AWS call.
    """
    one = One()
    one.config = Config.load(
        env_name=env_name,
        runtime_name=RuntimeNameEnum.local.value,
    )
    stack_ctx_enum = StackCtxEnum(one=one)
    targets = {}
    for stack in list_entry_names(StackCtxEnum):
        stack_ctx = stack_ctx_enum.get(stack)
        targets[stack] = StackTarget(
            construct_id=stack_ctx.construct_id,
            console_url=one.config.get_cft_stack_url(stack_ctx.stack_name),
        )
    return targets


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

    :param construct_id: the stack to act on, or ``None`` for every stack
        (:attr:`CdkAction.all_option`).
    """
    sub_command, _, options = action.command.partition(" ")
    parts = ["cdk", sub_command]
    if construct_id is None:
        if action.all_option:
            parts.append(action.all_option)
    else:
        parts.extend([construct_id, "--exclusively"])
    if options:
        parts.append(options)
    if action.use_profile:
        parts.append(f"--profile {{{{env.{get_aws_profile_env_var(env_name)}}}}}")
    return " ".join(parts)


def get_run_script(
    action: CdkAction,
    env_name: str,
    targets: list[StackTarget],
    select_all: bool,
) -> str:
    """
    The script of a task: print the console URL of every stack it acts on, so the
    user can watch it in the console, then print the cdk command and run it.

    :param targets: the stacks the task acts on.
    :param select_all: ``True`` for the ``all`` tasks (``--all``).
    """
    lines = ["echo '--- CloudFormation console ---'"]
    for target in targets:
        lines.append(f"echo '{target.construct_id}: {target.console_url}'")
    construct_id = None if select_all else targets[0].construct_id
    command = get_cdk_command(action, env_name, construct_id)
    lines.append("echo '--- Run command ---'")
    lines.append(f"echo '{command}'")
    lines.append(command)
    return "\n".join(lines)


def _render_task(
    action: CdkAction,
    env_name: str,
    stack_slug: str,
    targets: list[StackTarget],
) -> str:
    select_all = stack_slug == ALL
    target = "all stacks" if select_all else f"stack {stack_slug}"
    summary = action.summary.format(target=target, env=env_name)
    task_name = get_task_name(action.name, env_name, stack_slug)
    script = get_run_script(action, env_name, targets, select_all)
    lines = [
        f'[tasks."{task_name}"]',
        f'description = "{action.emoji} {summary}"',
        'dir = "cdk"',
        f'env = {{ {ENV_NAME_VAR} = "{env_name}" }}',
        'depends = ["inst"]',
        f'run = """\n{script}\n"""',
    ]
    return "\n".join(lines)


def render_cdk_tasks(env_stack_targets: dict[str, dict[str, StackTarget]]) -> str:
    """
    Render the whole generated block, markers included.

    :param env_stack_targets: for each environment, its stacks by entry name, see
        :func:`get_stack_targets`. Tasks follow its order: by environment, then
        the ``all`` tasks, then each stack.

    :raises ValueError: see :func:`validate_stacks`.
    """
    header = (
        f"{BEGIN_MARKER}\n"
        "# Generated by ``mise run cdk-gen-tasks`` from StackCtxEnum. Do not edit by hand."
    )
    parts = [header]
    for env_name, stack_targets in env_stack_targets.items():
        validate_stacks(list(stack_targets))
        groups = [(ALL, list(stack_targets.values()))]
        for stack, target in stack_targets.items():
            groups.append((to_stack_slug(stack), [target]))
        for stack_slug, targets in groups:
            for action in CDK_ACTIONS:
                task = _render_task(
                    action=action,
                    env_name=env_name,
                    stack_slug=stack_slug,
                    targets=targets,
                )
                parts.append(task)
    parts.append(END_MARKER)
    return "\n\n".join(parts)


def render_project_cdk_tasks() -> str:
    """
    :func:`render_cdk_tasks` for every stack of this project in every environment.
    """
    env_stack_targets = {
        member.value: get_stack_targets(member.value) for member in EnvNameEnum
    }
    return render_cdk_tasks(env_stack_targets)


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
