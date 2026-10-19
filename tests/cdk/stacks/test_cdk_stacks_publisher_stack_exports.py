# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stacks.publisher_stack_exports import STACK_NAMES
from cookiecutter_aws_cdk_demo.cdk.stacks.publisher_stack_exports import (
    PublisherStackExports,
)

import ast

import aws_cdk as cdk

from cookiecutter_aws_cdk_demo.env import EnvNameEnum
from cookiecutter_aws_cdk_demo.paths import path_enum
from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One
from cookiecutter_aws_cdk_demo.cdk.stack_enum import StackEnum


def test_copy_pasteable():
    """
    The module imports only the standard library, so another project can copy it.
    """
    path = path_enum.dir_package / "cdk" / "stacks" / "publisher_stack_exports.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert node.module.split(".")[0] in ["typing", "mypy_boto3_cloudformation"]
        elif isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name in ["typing", "dataclasses"]


def test_stack_names():
    """
    The literal stack names match the config of every environment.
    """
    assert set(STACK_NAMES) == {member.value for member in EnvNameEnum}
    for env_name, stack_name in STACK_NAMES.items():
        config = Config.load(env_name=env_name, runtime_name="local")
        assert stack_name == config.cft_stack_name_publisher


def test_output_keys():
    """
    Every property reads an output the stack really creates.
    """
    se = StackEnum(app=cdk.App(), one=One())
    template = cdk.assertions.Template.from_stack(se.publisher)
    outputs = template.to_json()["Outputs"]
    response = {
        "Stacks": [
            {
                "StackName": STACK_NAMES["dev"],
                "Outputs": [
                    {
                        "OutputKey": key,
                        "OutputValue": f"value-of-{key}",
                        **(
                            {"ExportName": value["Export"]["Name"]}
                            if "Export" in value
                            else {}
                        ),
                    }
                    for key, value in outputs.items()
                ],
            }
        ]
    }
    exports = PublisherStackExports.from_describe_stacks_response(
        env_name="dev", response=response
    )
    assert exports.stack_name == STACK_NAMES["dev"]
    assert exports.publisher_role_arn == "value-of-PublisherRoleArn"
    assert "value-of-PublisherRoleArn" in exports.exports.values()


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.stacks.publisher_stack_exports",
        preview=False,
    )
