# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.one.one_02_boto_ses import get_aws_profile_env_var
from cookiecutter_aws_cdk_demo.one.one_02_boto_ses import OneBotoSesMixin

import pytest

import boto3

from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One


def test_get_aws_profile_env_var():
    assert get_aws_profile_env_var("prd") == "AWS_PROFILE_PRD"


@pytest.mark.parametrize(
    "ci,profile,expected",
    [
        (False, "my_dev", "my_dev"),
        (False, None, None),
        (True, "my_dev", None),
    ],
)
def test_bsm(monkeypatch, ci: bool, profile: str | None, expected: str | None):
    """
    Locally, ``AWS_PROFILE_<ENV>`` of the current environment picks the profile;
    otherwise the default chain. The region comes from the config; no AWS call.
    """
    if ci:
        monkeypatch.setenv("CI", "true")
    if profile is None:
        monkeypatch.delenv("AWS_PROFILE_DEV", raising=False)
    else:
        monkeypatch.setenv("AWS_PROFILE_DEV", profile)
    one = One()
    one.config = Config(
        project_name="my_project",
        env_name="dev",
        aws_account_id="111122223333",
        aws_region="us-west-2",
        log_level="DEBUG",
    )
    assert isinstance(one, OneBotoSesMixin)
    assert (one.bsm.profile_name or None) == expected
    assert one.bsm.region_name == "us-west-2"
    # the profile "my_dev" does not exist here, so only build a session without one
    if expected is None:
        assert isinstance(one.boto_ses, boto3.Session)
        assert one.aws_region == "us-west-2"


@pytest.mark.parametrize(
    "aws_account_id,aws_region,ok",
    [
        ("111122223333", "us-east-1", True),
        ("999999999999", "us-east-1", False),
        ("111122223333", "us-west-2", False),
    ],
)
def test_verify_boto_ses(
    config: Config,
    aws_account_id: str,
    aws_region: str,
    ok: bool,
):
    one = One()
    one.config = config
    # fake what the session reports, instead of calling STS
    one.aws_account_id = aws_account_id
    one.aws_region = aws_region
    if ok:
        one.verify_boto_ses()
    else:
        with pytest.raises(ValueError):
            one.verify_boto_ses()


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.one.one_02_boto_ses",
        preview=False,
    )
