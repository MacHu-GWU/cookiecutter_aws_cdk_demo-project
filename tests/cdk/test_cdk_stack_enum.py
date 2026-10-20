# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stack_enum import StackEnum

import aws_cdk as cdk

from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One
from cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum import StackCtxEnum
from cookiecutter_aws_cdk_demo.cdk.stack_ctx_enum import list_entry_names
from cookiecutter_aws_cdk_demo.cdk.stacks.alerts_stack import AlertsStack
from cookiecutter_aws_cdk_demo.cdk.stacks.publisher_stack.stack import PublisherStack


def _make_stack_enum(config: Config, **app_kwargs) -> StackEnum:
    one = One()
    one.config = config
    return StackEnum(app=cdk.App(**app_kwargs), one=one)


class TestStackEnum:
    def test_entries_match_stack_ctx_enum(self):
        """
        Layer 2 has exactly the entries of layer 1, in the same order.
        """
        assert list_entry_names(StackEnum) == list_entry_names(StackCtxEnum)

    def test_stacks(self, config: Config):
        """
        Each stack takes its names and environment from its stack context.
        """
        se = _make_stack_enum(config)
        stack_ctx = se.one.stack_ctx_enum.publisher
        stack = se.publisher
        assert isinstance(stack, PublisherStack)
        assert isinstance(se.alerts, AlertsStack)
        assert stack.node.id == stack_ctx.construct_id
        assert stack.stack_name == "my-project-dev-publisher"
        assert stack.account == "111122223333"
        assert stack.region == "us-east-1"
        # the dependency is wired by attribute access
        assert stack.alert_topic is se.alerts.alert_topic
        assert se.get_all() == [se.alerts, se.publisher]
        # CDK adds the stack dependency when it resolves the reference, at synth
        se.app.synth()
        assert se.alerts in stack.dependencies

    def test_synth(self, config: Config, tmp_path):
        se = _make_stack_enum(config, outdir=str(tmp_path))
        se.synth()
        names = sorted(p.name for p in tmp_path.glob("*.template.json"))
        assert names == [
            "my-project-dev-alerts.template.json",
            "my-project-dev-publisher.template.json",
        ]


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.stack_enum",
        preview=False,
    )
