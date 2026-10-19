# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stacks.alerts_stack import AlertsStack

import aws_cdk as cdk
from aws_cdk.assertions import Template

from cookiecutter_aws_cdk_demo.config.api import Config


def test_alerts_stack(config: Config):
    """
    The topic, the parameter, and the export are named by the config.
    """
    stack = AlertsStack(
        scope=cdk.App(),
        id="Alerts",
        stack_name=config.cft_stack_name_alerts,
        env=cdk.Environment(account=config.aws_account_id, region=config.aws_region),
        config=config,
    )
    assert stack.config is config
    template = Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::SNS::Topic",
        {"TopicName": "my-project-dev-alerts"},
    )
    template.has_resource_properties(
        "AWS::SSM::Parameter",
        {"Name": "/my-project-dev/log-level", "Type": "String", "Value": "DEBUG"},
    )
    template.has_output(
        "AlertTopicArn",
        {"Export": {"Name": "my-project-dev-alert-topic-arn"}},
    )


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.stacks.alerts_stack",
        preview=False,
    )
