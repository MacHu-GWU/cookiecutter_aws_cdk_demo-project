# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stacks.param_stack import ParamStack

import aws_cdk as cdk
from aws_cdk.assertions import Template

from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One


def test_param_stack():
    """
    The stack holds exactly one SSM parameter, named after the project, valued ``hello world``.
    """
    one = One()
    one.config = Config(project_name="my_project", env_name="dev", hello_value="hi")
    stack = ParamStack(
        scope=cdk.App(),
        id="my-project-param",
        one=one,
    )
    assert stack.stack_name == "my-project-param"
    template = Template.from_stack(stack)
    template.resource_count_is("AWS::SSM::Parameter", 1)
    template.has_resource_properties(
        "AWS::SSM::Parameter",
        {
            "Name": "/my-project/hello",
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
