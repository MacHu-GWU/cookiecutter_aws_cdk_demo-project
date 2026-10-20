# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.one.one_02_boto_ses import get_aws_profile_env_var
from cookiecutter_aws_cdk_demo.one.one_02_boto_ses import OneBotoSesMixin

import pytest

import boto3

from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One


def test_get_aws_profile_env_var():
    assert get_aws_profile_env_var("prd") == "AWS_PROFILE_FOR_PRD"


@pytest.mark.parametrize(
    "ci,profile,expected",
    [
        (False, "my_dev", "my_dev"),
        (False, None, None),
        (True, "my_dev", None),
    ],
)
def test_bsm(
    monkeypatch, config: Config, ci: bool, profile: str | None, expected: str | None
):
    """
    Locally, ``AWS_PROFILE_FOR_<ENV>`` of the current environment picks the profile;
    otherwise the default chain. The region comes from the config; no AWS call.
    """
    if ci:
        monkeypatch.setenv("CI", "true")
    if profile is None:
        monkeypatch.delenv("AWS_PROFILE_FOR_DEV", raising=False)
    else:
        monkeypatch.setenv("AWS_PROFILE_FOR_DEV", profile)
    one = One()
    one.config = config.model_copy(update={"aws_region": "us-west-2"})
    assert isinstance(one, OneBotoSesMixin)
    assert (one.bsm.profile_name or None) == expected
    assert one.bsm.region_name == "us-west-2"
    # the profile "my_dev" does not exist here, so only build a session without one
    if expected is None:
        assert isinstance(one.boto_ses, boto3.Session)
        assert one.boto_ses.region_name == "us-west-2"


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.one.one_02_boto_ses",
        preview=False,
    )
