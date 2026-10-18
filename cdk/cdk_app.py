#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The CDK app entry point, run by the cdk CLI (see ``cdk.json``).
"""

from cookiecutter_aws_cdk_demo.cdk.stack_enum import stack_enum

stack_enum.synth()
