# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.mise_tasks import BEGIN_MARKER
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import END_MARKER
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import CDK_ACTIONS
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import validate_stacks
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import StackTarget
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import get_stack_targets
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import get_task_name
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import render_cdk_tasks
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import render_project_cdk_tasks
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import replace_cdk_tasks_block
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import update_mise_toml

import pytest

import tomllib

from cookiecutter_aws_cdk_demo.paths import path_enum


@pytest.mark.parametrize(
    "stacks",
    [
        ["all"],
        ["my_b", "my-b"],
    ],
)
def test_validate_stacks_error(stacks: list[str]):
    with pytest.raises(ValueError):
        validate_stacks(stacks)


def test_get_stack_targets():
    targets = get_stack_targets("prd")
    assert list(targets) == ["alerts", "publisher"]
    target = targets["alerts"]
    assert target.construct_id == "cookiecutter-aws-cdk-demo-prd-alerts"
    assert "stackinfo?filteringText=cookiecutter-aws-cdk-demo-prd-alerts&" in (
        target.console_url
    )


def test_get_task_name():
    assert get_task_name("up", "dev", "all") == "cdk-up-dev-all"
    assert get_task_name("up", "dev", "my-b") == "cdk-up-dev-my-b-stack"


def _target(construct_id: str) -> StackTarget:
    return StackTarget(construct_id=construct_id, console_url=f"https://{construct_id}")


def test_render_cdk_tasks():
    """
    The block is valid TOML: per environment, four tasks for ``all`` and four per
    stack, each run in ``cdk/`` with ``ENV_NAME`` set. A task prints the console
    URL of exactly the stacks it acts on, then the cdk command, then runs it.
    """
    block = render_cdk_tasks(
        {
            "dev": {"a": _target("p-dev-a"), "my_b": _target("p-dev-my-b")},
            "prd": {"a": _target("p-prd-a"), "my_b": _target("p-prd-my-b")},
        }
    )
    assert block.startswith(BEGIN_MARKER)
    assert block.endswith(END_MARKER)
    tasks = tomllib.loads(block)["tasks"]
    assert len(tasks) == 2 * 3 * len(CDK_ACTIONS)
    for task in tasks.values():
        assert task["dir"] == "cdk"

    # fmt: off
    task = tasks["cdk-synth-dev-all"]
    assert task["env"] == {"ENV_NAME": "dev"}
    assert task["run"].splitlines() == [
        "echo '--- CloudFormation console ---'",
        "echo 'p-dev-a: https://p-dev-a'",
        "echo 'p-dev-my-b: https://p-dev-my-b'",
        "echo '--- Run command ---'",
        "echo 'cdk synth'",
        "cdk synth",
    ]

    task = tasks["cdk-up-prd-all"]
    assert task["env"] == {"ENV_NAME": "prd"}
    assert task["run"].splitlines()[-1] == "cdk deploy --all --require-approval never --profile {{env.AWS_PROFILE_FOR_PRD}}"

    task = tasks["cdk-plan-dev-my-b-stack"]
    assert task["run"].splitlines() == [
        "echo '--- CloudFormation console ---'",
        "echo 'p-dev-my-b: https://p-dev-my-b'",
        "echo '--- Run command ---'",
        "echo 'cdk diff p-dev-my-b --exclusively --method auto --profile {{env.AWS_PROFILE_FOR_DEV}}'",
        "cdk diff p-dev-my-b --exclusively --method auto --profile {{env.AWS_PROFILE_FOR_DEV}}",
    ]

    task = tasks["cdk-down-prd-a-stack"]
    assert task["run"].splitlines()[-1] == "cdk destroy p-prd-a --exclusively --force --profile {{env.AWS_PROFILE_FOR_PRD}}"
    # fmt: on


@pytest.mark.parametrize(
    "text",
    [
        "no markers",
        f"{END_MARKER}\n{BEGIN_MARKER}\n",
    ],
)
def test_replace_cdk_tasks_block_error(text: str):
    with pytest.raises(ValueError):
        replace_cdk_tasks_block(text, "")


def test_update_mise_toml(tmp_path):
    path = tmp_path / "mise.toml"
    path.write_text(f"[env]\n\n{BEGIN_MARKER}\nold\n{END_MARKER}\n# tail\n")
    block = render_cdk_tasks({"dev": {"a": _target("p-dev-a")}})
    assert update_mise_toml(path, block) is True
    text = path.read_text()
    assert text.startswith("[env]\n\n")
    assert text.endswith(f"{END_MARKER}\n# tail\n")
    assert "old" not in text
    assert update_mise_toml(path, block) is False


def test_mise_toml_is_up_to_date():
    """
    ``mise.toml`` holds the tasks of exactly the stacks of StackCtxEnum in every
    environment. If this fails, run ``mise run cdk-gen-tasks``.
    """
    text = path_enum.path_mise_toml.read_text(encoding="utf-8")
    assert render_project_cdk_tasks() in text


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.mise_tasks",
        preview=False,
    )
