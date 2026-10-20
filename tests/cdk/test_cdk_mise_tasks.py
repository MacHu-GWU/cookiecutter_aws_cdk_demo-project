# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.mise_tasks import BEGIN_MARKER
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import END_MARKER
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import CDK_ACTIONS
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import validate_stacks
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import get_construct_ids
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


def test_get_construct_ids():
    assert get_construct_ids("prd") == {
        "alerts": "cookiecutter-aws-cdk-demo-prd-alerts",
        "publisher": "cookiecutter-aws-cdk-demo-prd-publisher",
    }


def test_get_task_name():
    assert get_task_name("up", "dev", "all") == "cdk-up-dev-all"
    assert get_task_name("up", "dev", "my-b") == "cdk-up-dev-my-b-stack"


def test_render_cdk_tasks():
    """
    The block is valid TOML: per environment, four tasks for ``all`` and four per
    stack, each a plain cdk command in ``cdk/`` with ``ENV_NAME`` set.
    """
    block = render_cdk_tasks(
        {
            "dev": {"a": "p-dev-a", "my_b": "p-dev-my-b"},
            "prd": {"a": "p-prd-a", "my_b": "p-prd-my-b"},
        }
    )
    assert block.startswith(BEGIN_MARKER)
    assert block.endswith(END_MARKER)
    tasks = tomllib.loads(block)["tasks"]
    assert len(tasks) == 2 * 3 * len(CDK_ACTIONS)
    for task in tasks.values():
        assert task["dir"] == "cdk"
    task = tasks["cdk-synth-dev-all"]
    assert task["run"] == "cdk synth --all"
    assert task["env"] == {"ENV_NAME": "dev"}
    task = tasks["cdk-up-prd-all"]
    assert task["run"] == (
        "cdk deploy --all --require-approval never"
        " --profile {{env.AWS_PROFILE_FOR_PRD}}"
    )
    assert task["env"] == {"ENV_NAME": "prd"}
    task = tasks["cdk-plan-dev-my-b-stack"]
    assert task["run"] == (
        "cdk diff p-dev-my-b --exclusively --method auto"
        " --profile {{env.AWS_PROFILE_FOR_DEV}}"
    )
    task = tasks["cdk-down-prd-a-stack"]
    assert task["run"] == (
        "cdk destroy p-prd-a --exclusively --force --profile {{env.AWS_PROFILE_FOR_PRD}}"
    )


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
    block = render_cdk_tasks({"dev": {"a": "p-dev-a"}})
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
