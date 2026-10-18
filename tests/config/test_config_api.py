# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.config import api


def test():
    _ = api
    _ = api.Config


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.config.api",
        preview=False,
    )
