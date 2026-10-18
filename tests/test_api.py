# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo import api


def test():
    _ = api
    _ = api.DEFAULT_NAME
    _ = api.add_two
    _ = api.greet
    _ = api.Greeter
    _ = api.example_package_1
    _ = api.example_package_1.multi_two


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.api",
        preview=False,
    )
