# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.one.one_02_boto_ses import OneBotoSesMixin

import pytest

import boto3

from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One


def test_boto_ses(monkeypatch):
    """
    The session follows the standard chain; building it makes no AWS call.
    """
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    one = One()
    assert isinstance(one, OneBotoSesMixin)
    assert isinstance(one.boto_ses, boto3.Session)
    assert one.aws_region == "us-east-1"


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
