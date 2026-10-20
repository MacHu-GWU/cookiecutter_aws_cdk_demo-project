# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.stacks import publisher_stack_exports

from cookiecutter_aws_cdk_demo.tests.helper import check_stack_exports


def test():
    check_stack_exports(
        module=publisher_stack_exports,
        exports_class=publisher_stack_exports.PublisherStackExports,
    )


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_unit_test

    run_unit_test(__file__)
