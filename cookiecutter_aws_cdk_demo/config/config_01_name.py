# -*- coding: utf-8 -*-

"""
Every AWS resource name of the project, with its console URL and ARN.

Names are built here, never in the CDK code, so stacks, scripts, and tests all
refer to the same value (``one.config.ssm_param_name_hello``) instead of
repeating a string template.

Naming pattern: ``<resource type>_<attribute>_<short name>``, such as
``cft_stack_name_param``, ``cft_stack_url_param``, ``ssm_param_arn_hello``.
CloudFormation stacks have no ARN property, because the ARN ends in a random ID
assigned at creation.
"""

from __future__ import annotations

import typing as T
from functools import cached_property

if T.TYPE_CHECKING:  # pragma: no cover
    from .config_00_main import Config


class ConfigNameMixin:
    """
    Resource names, console URLs, and ARNs derived from the config values.
    """

    # --------------------------------------------------------------------------
    # Prefixes
    # --------------------------------------------------------------------------
    @cached_property
    def project_name_snake(self: Config) -> str:
        """
        Project name in snake_case, such as ``my_project``.
        """
        return self.project_name.replace("-", "_")

    @cached_property
    def project_name_slug(self: Config) -> str:
        """
        Project name in slug-case, such as ``my-project``.
        """
        return self.project_name_snake.replace("_", "-")

    @cached_property
    def prefix_name_slug(self: Config) -> str:
        """
        Prefix of every resource name of this environment, such as ``my-project-dev``.
        """
        return f"{self.project_name_slug}-{self.env_name}"

    # --------------------------------------------------------------------------
    # CloudFormation stacks
    # --------------------------------------------------------------------------
    def get_cft_stack_name(self: Config, short_name: str) -> str:
        """
        The name of a stack, ``<prefix_name_slug>-<short_name>``; also its construct ID.
        """
        return f"{self.prefix_name_slug}-{short_name}"

    def get_cft_stack_url(self: Config, stack_name: str) -> str:
        """
        The CloudFormation console URL that lists the stack.
        """
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/cloudformation/home"
            f"?region={self.aws_region}#/stacks?filteringText={stack_name}"
            f"&filteringStatus=active&viewNested=true"
        )

    @cached_property
    def cft_stack_name_param(self: Config) -> str:
        """
        Name of the sample stack, such as ``my-project-dev-param``.
        """
        return self.get_cft_stack_name(self.stack_short_name_param)

    @cached_property
    def cft_stack_url_param(self: Config) -> str:
        """
        Console URL of :attr:`cft_stack_name_param`.
        """
        return self.get_cft_stack_url(self.cft_stack_name_param)

    # --------------------------------------------------------------------------
    # SSM parameters
    # --------------------------------------------------------------------------
    @cached_property
    def ssm_param_name_hello(self: Config) -> str:
        """
        Name of the sample SSM parameter, such as ``/my-project-dev/hello``.
        """
        return f"/{self.prefix_name_slug}/hello"

    @cached_property
    def ssm_param_url_hello(self: Config) -> str:
        """
        Console URL of :attr:`ssm_param_name_hello`.
        """
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/systems-manager"
            f"/parameters{self.ssm_param_name_hello}/description"
            f"?region={self.aws_region}&tab=Table"
        )

    @cached_property
    def ssm_param_arn_hello(self: Config) -> str:
        """
        ARN of :attr:`ssm_param_name_hello`.
        """
        return (
            f"arn:aws:ssm:{self.aws_region}:{self.aws_account_id}"
            f":parameter{self.ssm_param_name_hello}"
        )
