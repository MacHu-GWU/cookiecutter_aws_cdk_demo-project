# -*- coding: utf-8 -*-

"""
A sample stack with a single SSM parameter, used to prove the deploy workflow end to end.
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from ...config import Config


class ParamStack(cdk.Stack):
    """
    Holds one SSM String parameter, ``/<project_name_slug>/hello``, with the value ``hello world``.

    The stack is environment-agnostic (no ``env=``), so it synthesizes without AWS
    credentials, and the target account and region come from ``AWS_PROFILE`` at deploy time.

    :param scope: the CDK app.
    :param id: the construct ID, also the CloudFormation stack name.
    :param config: the project configuration.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        config: Config,
        **kwargs,
    ) -> None:
        super().__init__(scope=scope, id=id, **kwargs)
        self.config = config
        self.s01_create_ssm_parameter()

    def s01_create_ssm_parameter(self) -> None:
        """
        Create the SSM parameter.
        """
        self.ssm_param_hello = ssm.StringParameter(
            self,
            "SsmParamHello",
            parameter_name=f"/{self.config.project_name_slug}/hello",
            string_value="hello world",
        )
