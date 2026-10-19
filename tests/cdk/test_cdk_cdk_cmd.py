# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import ALL
from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import CDK_ACTION_MAP
from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import to_stack_slug
from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import get_stack_ctx_list
from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import build_cdk_cmd
from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import make_parser

import pytest

from cookiecutter_aws_cdk_demo.config.api import Config
from cookiecutter_aws_cdk_demo.one.api import One


def test_to_stack_slug():
    assert to_stack_slug("my_stack") == "my-stack"


@pytest.mark.parametrize(
    "action,stack,expected",
    [
        (
            "synth",
            "alerts",
            "cdk synth MyProjectDevAlerts --exclusively",
        ),
        (
            "plan",
            ALL,
            "cdk diff MyProjectDevAlerts MyProjectDevPublisher --method auto",
        ),
        (
            "up",
            "publisher",
            "cdk deploy MyProjectDevPublisher --exclusively --require-approval never",
        ),
        (
            "down",
            ALL,
            "cdk destroy MyProjectDevAlerts MyProjectDevPublisher --force",
        ),
    ],
)
def test_build_cdk_cmd(config: Config, action: str, stack: str, expected: str):
    one = One()
    one.config = config
    stack_ctx_list = get_stack_ctx_list(one.stack_ctx_enum, stack)
    cmd = build_cdk_cmd(CDK_ACTION_MAP[action], stack, stack_ctx_list)
    assert sorted(cmd.to_args()) == sorted(expected.split(" "))
    assert cmd.to_args()[:2] == expected.split(" ")[:2]


def test_make_parser():
    args = make_parser().parse_args(["up", "alerts"])
    assert (args.action, args.stack) == ("up", "alerts")
    with pytest.raises(SystemExit):
        make_parser().parse_args(["up", "unknown"])


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.cdk.cdk_cmd",
        preview=False,
    )
