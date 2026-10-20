# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk import api


def test():
    _ = api
    _ = api.AlertsStack
    _ = api.AlertsStackExports
    _ = api.PublisherStack
    _ = api.PublisherStackExports
    _ = api.StackCtxEnum
    _ = api.list_entry_names
    _ = api.StackEnum
    _ = api.ALL
    _ = api.CdkAction
    _ = api.CDK_ACTIONS
    _ = api.render_cdk_tasks
    _ = api.render_project_cdk_tasks
    _ = api.update_mise_toml


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.api",
        preview=False,
    )
