# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo import api


def test():
    _ = api
    _ = api.Config
    _ = api.config
    _ = api.cdk
    _ = api.cdk.stack_enum


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.api",
        preview=False,
    )
