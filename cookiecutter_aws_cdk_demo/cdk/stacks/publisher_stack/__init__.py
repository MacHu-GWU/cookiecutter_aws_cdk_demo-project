# -*- coding: utf-8 -*-

"""
The publisher stack: an IAM role allowed to publish to the alert topic of
:mod:`~cookiecutter_aws_cdk_demo.cdk.stacks.alerts_stack`, and an SSM parameter
that records the topic ARN. Every resource is free.

It shows the folder form of a stack, for a stack too large for one file:

- ``stack.py``: the :class:`~cookiecutter_aws_cdk_demo.cdk.stacks.publisher_stack.stack.PublisherStack`
  class. Its ``__init__`` takes the standard arguments, the config, and the
  resources of other stacks it uses, then calls one ``create_*`` method per mixin.
- ``stack_01_iam.py``, ``stack_02_ssm.py``: one mixin per group of resources,
  numbered in creation order.

The topic arrives as an explicit argument, so CDK turns the reference into an
export of the alerts stack and an import here, and deploys the alerts stack first.
"""
