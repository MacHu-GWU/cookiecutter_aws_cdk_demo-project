# -*- coding: utf-8 -*-

"""
Rewrite the <cdk-stack-tasks> block of mise.toml from the entries of StackCtxEnum
and the members of EnvNameEnum.
"""

from cookiecutter_aws_cdk_demo.paths import path_enum
from cookiecutter_aws_cdk_demo.env import EnvNameEnum
from cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum import StackCtxEnum
from cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum import list_entry_names
from cookiecutter_aws_cdk_demo.cdk.mise_tasks import update_mise_toml


def main():
    stacks = list_entry_names(StackCtxEnum)
    env_names = [member.value for member in EnvNameEnum]
    changed = update_mise_toml(
        path=path_enum.path_mise_toml,
        stacks=stacks,
        env_names=env_names,
    )
    if changed:
        print(
            f"Updated {path_enum.path_mise_toml} for stacks {stacks} x envs {env_names}"
        )
    else:
        print(f"{path_enum.path_mise_toml} is already up to date")


if __name__ == "__main__":
    main()
