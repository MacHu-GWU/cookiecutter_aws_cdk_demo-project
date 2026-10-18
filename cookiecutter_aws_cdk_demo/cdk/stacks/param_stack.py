# -*- coding: utf-8 -*-

"""
A sample stack with a single SSM parameter, used to prove the deploy workflow end to end.
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from ...config.api import Config


class ParamStack(cdk.Stack):
    """
    Holds one SSM String parameter, ``config.ssm_param_name_hello``, valued ``config.hello_value``.

    Every stack takes the config as a parameter and keeps it as ``self.config``.
    It reads names and values only from there, never builds a name itself, and
    makes no AWS call, so the same config always synthesizes the same template.

    :param scope: the CDK app.
    :param id: the construct ID, which is also the stack name, ``config.cft_stack_name_param``.
    :param config: the config of the environment being deployed.
    :param kwargs: passed to ``aws_cdk.Stack``, such as ``env``.
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
            parameter_name=self.config.ssm_param_name_hello,
            string_value=self.config.hello_value,
        )
