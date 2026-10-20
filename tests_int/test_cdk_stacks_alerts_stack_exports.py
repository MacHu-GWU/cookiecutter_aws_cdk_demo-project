# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stacks import alerts_stack_exports

from cookiecutter_aws_cdk_demo.tests.helper import check_stack_exports


def test():
    check_stack_exports(
        module=alerts_stack_exports,
        exports_class=alerts_stack_exports.AlertsStackExports,
    )


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_unit_test

    run_unit_test(__file__)
