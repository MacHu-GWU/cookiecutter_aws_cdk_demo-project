# -*- coding: utf-8 -*-

"""
Rewrite the <cdk-stack-tasks> block of mise.toml from the stacks in StackEnum.
"""

from cookiecutter_aws_cdk_demo.paths import path_enum
from cookiecutter_aws_cdk_demo.cdk.stack_enum import stack_enum
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import update_mise_toml


def main():
    stack_ids = [stack.node.id for stack in stack_enum.stacks]
    changed = update_mise_toml(
        path=path_enum.path_mise_toml,
        stack_ids=stack_ids,
    )
    if changed:
        print(f"Updated {path_enum.path_mise_toml} for stacks: {stack_ids}")
    else:
        print(f"{path_enum.path_mise_toml} is already up to date")


if __name__ == "__main__":
    main()
