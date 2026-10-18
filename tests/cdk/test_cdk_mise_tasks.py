# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.mise_tasks import ALL
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import BEGIN_MARKER
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import END_MARKER
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import CDK_ACTIONS
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import validate_short_names
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import get_stack_selector
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import render_cdk_tasks
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import replace_cdk_tasks_block
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import update_mise_toml

import pytest

import tomllib

from cookiecutter_aws_cdk_demo.paths import path_enum
from cookiecutter_aws_cdk_demo.cdk.stack_enum import stack_enum


@pytest.mark.parametrize(
    "short_names",
    [
        [ALL],
        ["a", "b", "a"],
        ["param", "big-param"],
    ],
)
def test_validate_short_names_error(short_names: list[str]):
    with pytest.raises(ValueError):
        validate_short_names(short_names)


def test_get_stack_selector():
    assert get_stack_selector("p", "param") == "p-*-param"


def test_render_cdk_tasks():
    """
    The block is valid TOML with five tasks for ``all`` and five per stack.
    """
    block = render_cdk_tasks("p", ["a", "b"])
    assert block.startswith(BEGIN_MARKER)
    assert block.endswith(END_MARKER)
    tasks = tomllib.loads(block)["tasks"]
    assert len(tasks) == 3 * len(CDK_ACTIONS)
    assert tasks["cdk-up-all"]["run"] == "cdk deploy --all --require-approval never"
    assert tasks["cdk-up-a"]["run"] == (
        "cdk deploy 'p-*-a' --exclusively --require-approval never"
    )
    assert tasks["cdk-down-ask-b"]["run"] == "cdk destroy 'p-*-b' --exclusively"
    for task in tasks.values():
        assert task["dir"] == "cdk"


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
    assert update_mise_toml(path, "p", ["a"]) is True
    text = path.read_text()
    assert text.startswith("[env]\n\n")
    assert text.endswith(f"{END_MARKER}\n# tail\n")
    assert "old" not in text
    assert update_mise_toml(path, "p", ["a"]) is False


def test_mise_toml_is_up_to_date():
    """
    ``mise.toml`` holds the tasks of exactly the stacks in StackEnum.
    If this fails, run ``mise run cdk-gen-tasks``.
    """
    project_name_slug = stack_enum.config.project_name_slug
    short_names = stack_enum.stack_short_names
    text = path_enum.path_mise_toml.read_text(encoding="utf-8")
    assert render_cdk_tasks(project_name_slug, short_names) in text


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.mise_tasks",
        preview=False,
    )
