# -*- coding: utf-8 -*-

"""
Rewrite the <cdk-stack-tasks> block of mise.toml from the stacks in StackEnum.
"""

from cookiecutter_aws_cdk_demo.paths import path_enum
from cookiecutter_aws_cdk_demo.cdk.stack_enum import stack_enum
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import update_mise_toml


def main():
    short_names = stack_enum.stack_short_names
    changed = update_mise_toml(
        path=path_enum.path_mise_toml,
        project_name_slug=stack_enum.config.project_name_slug,
        short_names=short_names,
    )
    if changed:
        print(f"Updated {path_enum.path_mise_toml} for stacks: {short_names}")
    else:
        print(f"{path_enum.path_mise_toml} is already up to date")


if __name__ == "__main__":
    main()
