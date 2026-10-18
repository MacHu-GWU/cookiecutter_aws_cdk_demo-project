#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The CDK app entry point, run by the cdk CLI (see ``cdk.json``).
"""

from cookiecutter_aws_cdk_demo.one.api import one
from cookiecutter_aws_cdk_demo.cdk.stack_enum import stack_enum

# Stop before synth if AWS_PROFILE points at another account or region than the config.
one.verify_boto_ses()
stack_enum.synth()
