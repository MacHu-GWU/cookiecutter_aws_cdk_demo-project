# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stack_enum import StackEnum
from cookiecutter_aws_cdk_demo.cdk.stack_enum import stack_enum

import pytest

import aws_cdk as cdk

from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One
from cookiecutter_aws_cdk_demo.cdk.stacks.param_stack import ParamStack


def _make_stack_enum(config: Config, **app_kwargs) -> StackEnum:
    one = One()
    one.config = config
    return StackEnum(app=cdk.App(**app_kwargs), one=one)


class TestStackEnum:
    def test_stacks(self, config: Config):
        """
        Every stack is found, named by the config, and bound to its account and region.
        """
        se = _make_stack_enum(config)
        assert se.stacks == [se.param_stack]
        assert isinstance(se.param_stack, ParamStack)
        assert se.param_stack.node.id == "my-project-dev-param"
        assert se.param_stack.stack_name == "my-project-dev-param"
        assert se.param_stack.account == "111122223333"
        assert se.param_stack.region == "us-east-1"
        assert se.stack_short_names == ["param"]

    def test_stack_short_names_error(self, config: Config):
        """
        A stack whose name does not start with the config prefix is rejected.
        """
        se = _make_stack_enum(config)
        se.param_stack = ParamStack(scope=se.app, id="other-name", config=config)
        with pytest.raises(ValueError):
            _ = se.stack_short_names

    def test_synth(self, config: Config, tmp_path):
        se = _make_stack_enum(config, outdir=str(tmp_path))
        se.synth()
        assert (tmp_path / "my-project-dev-param.template.json").exists()

    def test_stack_enum(self):
        assert (
            stack_enum.param_stack.stack_name == stack_enum.config.cft_stack_name_param
        )


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.stack_enum",
        preview=False,
    )
