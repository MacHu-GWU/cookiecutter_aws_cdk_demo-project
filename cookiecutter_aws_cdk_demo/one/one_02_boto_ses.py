# -*- coding: utf-8 -*-

"""
The AWS session part of ``one``: :attr:`~cookiecutter_aws_cdk_demo.one.one_02_boto_ses.OneBotoSesMixin.boto_ses`
and the facts and clients derived from it.
"""

from __future__ import annotations

import typing as T
from functools import cached_property

import boto3

if T.TYPE_CHECKING:  # pragma: no cover
    from .one_00_main import One


class OneBotoSesMixin:
    """
    Lazily built boto3 session and AWS clients.
    """

    @cached_property
    def boto_ses(self: One) -> boto3.Session:
        """
        The boto3 session every AWS call of this project goes through.

        It follows the standard credential chain, so it uses the same account as the
        cdk CLI: ``AWS_PROFILE`` from ``.env`` on a developer's machine, and the
        credentials the runner provides in CI. Branch on ``self.runtime`` here if the
        two ever need different settings.
        """
        return boto3.Session()

    @cached_property
    def aws_region(self: One) -> str | None:
        """
        The region of :attr:`boto_ses`, from the profile or ``AWS_REGION``.
        """
        return self.boto_ses.region_name

    @cached_property
    def aws_account_id(self: One) -> str:  # pragma: no cover
        """
        The AWS account ID of :attr:`boto_ses`; calls STS once.
        """
        return self.boto_ses.client("sts").get_caller_identity()["Account"]

    @cached_property
    def cloudformation_client(self: One):  # pragma: no cover
        """
        A CloudFormation client from :attr:`boto_ses`.
        """
        return self.boto_ses.client("cloudformation")

    @cached_property
    def ssm_client(self: One):  # pragma: no cover
        """
        An SSM client from :attr:`boto_ses`.
        """
        return self.boto_ses.client("ssm")

    def verify_boto_ses(self: One) -> None:
        """
        Check that :attr:`boto_ses` points at the account and region in ``config``.

        Run it before any deploy, so a wrong ``AWS_PROFILE`` stops the command
        instead of changing another account.

        :raises ValueError: the account ID or the region differs from the config.
        """
        expected = (self.config.aws_account_id, self.config.aws_region)
        actual = (self.aws_account_id, self.aws_region)
        if actual != expected:
            raise ValueError(
                f"the boto session points at account / region {actual}, "
                f"but config {self.config.env_name!r} expects {expected}; "
                "check AWS_PROFILE in .env"
            )
