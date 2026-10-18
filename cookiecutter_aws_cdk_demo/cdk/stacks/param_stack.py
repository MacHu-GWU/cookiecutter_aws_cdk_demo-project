# -*- coding: utf-8 -*-

"""
A sample stack with a single SSM parameter, used to prove the deploy workflow end to end.
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from ...one.api import One


class ParamStack(cdk.Stack):
    """
    Holds one SSM String parameter, ``/<project_name_slug>/hello``, valued ``config.hello_value``.

    The stack is environment-agnostic (no ``env=``), so it synthesizes without AWS
    credentials, and the target account and region come from ``AWS_PROFILE`` at deploy time.

    :param scope: the CDK app.
    :param id: the construct ID, also the CloudFormation stack name.
    :param one: the project singleton; the stack reads ``one.config``.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        one: One,
        **kwargs,
    ) -> None:
        super().__init__(scope=scope, id=id, **kwargs)
        self.one = one
        self.s01_create_ssm_parameter()

    def s01_create_ssm_parameter(self) -> None:
        """
        Create the SSM parameter.
        """
        self.ssm_param_hello = ssm.StringParameter(
            self,
            "SsmParamHello",
            parameter_name=f"/{self.one.config.project_name_slug}/hello",
            string_value=self.one.config.hello_value,
        )
