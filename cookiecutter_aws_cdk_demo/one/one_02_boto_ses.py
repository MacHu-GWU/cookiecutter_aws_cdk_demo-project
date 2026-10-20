# -*- coding: utf-8 -*-

"""
The AWS session part of ``one``: :attr:`~cookiecutter_aws_cdk_demo.one.one_02_boto_ses.OneBotoSesMixin.bsm`,
the boto session of the current environment, and the facts and clients derived from it.
"""

from __future__ import annotations

import typing as T
import os
from functools import cached_property

import boto3
from boto_session_manager.api import BotoSesManager

from ..runtime import RuntimeNameEnum

if T.TYPE_CHECKING:  # pragma: no cover
    from .one_00_main import One


def get_aws_profile_env_var(env_name: str) -> str:
    """
    The environment variable that names the local AWS profile of an environment,
    such as ``AWS_PROFILE_FOR_DEV`` for ``dev``; mise loads it from ``.env``.
    """
    return f"AWS_PROFILE_FOR_{env_name.upper()}"


class OneBotoSesMixin:
    """
    Lazily built boto3 session and AWS clients.
    """

    @cached_property
    def bsm(self: One) -> BotoSesManager:
        """
        The boto session of the current environment, in the region of its config.
        Creating it makes no AWS call.

        On a developer's machine (``runtime`` local), each environment usually has
        its own account and named profile: the session uses the profile named by
        ``AWS_PROFILE_FOR_<ENV>`` of the current environment, such as ``AWS_PROFILE_FOR_PRD``.
        Without it, and on any other runtime such as CI, it follows the standard
        credential chain (``AWS_PROFILE``, access keys, an assumed role).

        A wrong profile cannot change another account: every stack is bound to the
        ``aws_account_id`` of the config, and the cdk CLI refuses to deploy it with
        credentials of another account.
        """
        region_name = self.config.aws_region
        if self.runtime.current_runtime_name() == RuntimeNameEnum.local.value:
            env_var = get_aws_profile_env_var(self.env.current_env_name)
            profile_name = os.environ.get(env_var, "")
            if profile_name:
                return BotoSesManager(
                    profile_name=profile_name, region_name=region_name
                )
        return BotoSesManager(region_name=region_name)

    @cached_property
    def boto_ses(self: One) -> boto3.Session:
        """
        The boto3 session every AWS call of this project goes through, from :attr:`bsm`.
        """
        return self.bsm.boto_ses

    @cached_property
    def aws_region(self: One) -> str | None:
        """
        The region of :attr:`boto_ses`, the ``aws_region`` of the current config.
        """
        return self.boto_ses.region_name

    @cached_property
    def aws_account_id(self: One) -> str:  # pragma: no cover
        """
        The AWS account ID of :attr:`boto_ses`; calls STS once.
        """
        return self.bsm.aws_account_id

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

        Run it before any deploy, so a wrong ``AWS_PROFILE_FOR_<ENV>`` stops the command
        instead of changing another account.

        :raises ValueError: the account ID or the region differs from the config.
        """
        expected = (self.config.aws_account_id, self.config.aws_region)
        actual = (self.aws_account_id, self.aws_region)
        if actual != expected:
            raise ValueError(
                f"the boto session points at account / region {actual}, "
                f"but config {self.config.env_name!r} expects {expected}; "
                f"check {get_aws_profile_env_var(self.config.env_name)} in .env"
            )
