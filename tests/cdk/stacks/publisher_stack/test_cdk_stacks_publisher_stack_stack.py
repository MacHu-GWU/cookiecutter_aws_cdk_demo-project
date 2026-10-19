# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stacks.publisher_stack.stack import PublisherStack

import aws_cdk as cdk
from aws_cdk import aws_sns as sns
from aws_cdk.assertions import Template

from cookiecutter_aws_cdk_demo.config.api import Config


def test_publisher_stack(config: Config):
    """
    The role may publish to the given topic, and the parameter records its ARN.
    """
    app = cdk.App()
    topic_stack = cdk.Stack(app, "TopicStack")
    topic = sns.Topic(topic_stack, "Topic")
    stack = PublisherStack(
        scope=app,
        id="Publisher",
        stack_name=config.cft_stack_name_publisher,
        env=None,
        config=config,
        alert_topic=topic,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::IAM::Role",
        {"RoleName": "my-project-dev-publisher"},
    )
    template.resource_count_is("AWS::IAM::Policy", 1)
    template.has_resource_properties(
        "AWS::SSM::Parameter",
        {"Name": "/my-project-dev/alert-topic-arn"},
    )
    template.has_output(
        "PublisherRoleArn",
        {"Export": {"Name": "my-project-dev-publisher-role-arn"}},
    )


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.stacks.publisher_stack.stack",
        preview=False,
    )
