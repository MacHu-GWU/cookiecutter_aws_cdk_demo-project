# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.mise_tasks import BEGIN_MARKER
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import END_MARKER
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import validate_stacks
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import get_task_name
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import render_cdk_tasks
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import replace_cdk_tasks_block
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import update_mise_toml

import pytest

import tomllib

from cookiecutter_aws_cdk_demo.paths import path_enum
from cookiecutter_aws_cdk_demo.env import EnvNameEnum
from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import CDK_ACTIONS
from cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum import StackCtxEnum
from cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum import list_entry_names


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


def test_get_task_name():
    assert get_task_name("up", "dev", "all") == "cdk-up-dev-all"
    assert get_task_name("up", "dev", "my-b") == "cdk-up-dev-my-b-stack"


def test_render_cdk_tasks():
    """
    The block is valid TOML: per environment, four tasks for ``all`` and four per stack,
    each setting ``ENV_NAME``.
    """
    block = render_cdk_tasks(["a", "my_b"], ["dev", "prd"])
    assert block.startswith(BEGIN_MARKER)
    assert block.endswith(END_MARKER)
    tasks = tomllib.loads(block)["tasks"]
    assert len(tasks) == 2 * 3 * len(CDK_ACTIONS)
    task = tasks["cdk-up-prd-all"]
    assert task["run"] == ".venv/bin/python cdk/cdk_cmd.py up all"
    assert task["env"] == {"ENV_NAME": "prd"}
    task = tasks["cdk-down-dev-my-b-stack"]
    assert task["run"] == ".venv/bin/python cdk/cdk_cmd.py down my-b"
    assert task["env"] == {"ENV_NAME": "dev"}


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
    assert update_mise_toml(path, ["a"], ["dev"]) is True
    text = path.read_text()
    assert text.startswith("[env]\n\n")
    assert text.endswith(f"{END_MARKER}\n# tail\n")
    assert "old" not in text
    assert update_mise_toml(path, ["a"], ["dev"]) is False


def test_mise_toml_is_up_to_date():
    """
    ``mise.toml`` holds the tasks of exactly the entries of StackCtxEnum and the
    members of EnvNameEnum. If this fails, run ``mise run cdk-gen-tasks``.
    """
    stacks = list_entry_names(StackCtxEnum)
    env_names = [member.value for member in EnvNameEnum]
    text = path_enum.path_mise_toml.read_text(encoding="utf-8")
    assert render_cdk_tasks(stacks, env_names) in text


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.mise_tasks",
        preview=False,
    )
