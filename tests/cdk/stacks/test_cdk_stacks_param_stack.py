# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stacks.param_stack import ParamStack

import aws_cdk as cdk
from aws_cdk.assertions import Template

from cookiecutter_aws_cdk_demo.config.api import Config


def test_param_stack(config: Config):
    """
    The stack holds exactly one SSM parameter, with the name and value from the config.
    """
    stack = ParamStack(
        scope=cdk.App(),
        id=config.cft_stack_name_param,
        config=config,
    )
    assert stack.config is config
    template = Template.from_stack(stack)
    template.resource_count_is("AWS::SSM::Parameter", 1)
    template.has_resource_properties(
        "AWS::SSM::Parameter",
        {
            "Name": "/my-project-dev/hello",
            "Type": "String",
            "Value": "hi",
        },
    )


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.stacks.param_stack",
        preview=False,
    )
