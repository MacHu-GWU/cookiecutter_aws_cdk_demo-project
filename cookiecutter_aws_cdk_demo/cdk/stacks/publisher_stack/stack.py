# -*- coding: utf-8 -*-

"""
The :class:`PublisherStack` class; its resources are in the ``stack_0N_*.py`` mixins.
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import aws_sns as sns
from constructs import Construct

from ....config.api import Config
from .stack_01_iam import PublisherStackIamMixin
from .stack_02_ssm import PublisherStackSsmMixin


class PublisherStack(
    cdk.Stack,
    PublisherStackIamMixin,
    PublisherStackSsmMixin,
):
    """
    The publisher stack.

    :param scope: the CDK app.
    :param id: the construct ID, such as ``config.cft_stack_name_publisher``, the same as ``stack_name``.
    :param stack_name: the CloudFormation stack name, ``config.cft_stack_name_publisher``.
    :param env: the account and region of ``config``.
    :param config: the config of the environment being deployed.
    :param alert_topic: the alert topic of the
        :class:`~cookiecutter_aws_cdk_demo.cdk.stacks.alerts_stack.AlertsStack` of
        the same environment. It is an explicit argument, so the dependency is
        visible in the signature and wired in
        :class:`~cookiecutter_aws_cdk_demo.cdk.stack_enum.StackEnum`.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        stack_name: str,
        env: cdk.Environment,
        config: Config,
        alert_topic: sns.ITopic,
    ) -> None:
        super().__init__(
            scope=scope,
            id=id,
            stack_name=stack_name,
            env=env,
        )
        self.config = config
        self.alert_topic = alert_topic
        self.create_iam()
        self.create_ssm()
