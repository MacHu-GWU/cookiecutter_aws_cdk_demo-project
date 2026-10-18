# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stack_enum import StackEnum
from cookiecutter_aws_cdk_demo.cdk.stack_enum import stack_enum

import aws_cdk as cdk

from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One
from cookiecutter_aws_cdk_demo.cdk.stacks.param_stack import ParamStack


def _make_one() -> One:
    one = One()
    one.config = Config(project_name="my_project", env_name="dev", hello_value="hi")
    return one


class TestStackEnum:
    def test_stacks(self):
        """
        Every stack property is found, and each stack ID carries the project prefix.
        """
        se = StackEnum(
            app=cdk.App(),
            one=_make_one(),
        )
        stacks = se.stacks
        assert stacks == [se.param_stack]
        assert isinstance(se.param_stack, ParamStack)
        assert se.param_stack.node.id == "my-project-param"

    def test_synth(self, tmp_path):
        se = StackEnum(
            app=cdk.App(outdir=str(tmp_path)),
            one=_make_one(),
        )
        se.synth()
        assert (tmp_path / "my-project-param.template.json").exists()

    def test_stack_enum(self):
        assert stack_enum.param_stack.node.id == "cookiecutter-aws-cdk-demo-param"


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.stack_enum",
        preview=False,
    )
