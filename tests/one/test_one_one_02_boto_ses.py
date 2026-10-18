# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.one.one_02_boto_ses import OneBotoSesMixin

import boto3

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


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.one.one_02_boto_ses",
        preview=False,
    )
