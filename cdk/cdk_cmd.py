#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run one cdk action on one stack, or on every stack, of the environment that
``ENV_NAME`` selects, with the AWS profile of that environment. The ``cdk-*``
mise tasks call it::

    ENV_NAME=<dev|tst|prd> .venv/bin/python cdk/cdk_cmd.py <synth|plan|up|down> <stack|all>

See ``cookiecutter_aws_cdk_demo/cdk/cdk_cmd.py``.
"""

from cookiecutter_aws_cdk_demo.one.api import one
from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import make_parser
from cookiecutter_aws_cdk_demo.cdk.cdk_cmd import run_cdk_cmd

args = make_parser().parse_args()
run_cdk_cmd(
    one=one,
    action_name=args.action,
    stack=args.stack,
    dir_cdk=__file__,
)
