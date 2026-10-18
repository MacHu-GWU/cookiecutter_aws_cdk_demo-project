# -*- coding: utf-8 -*-

"""
Public API. Users import from here::

    from cookiecutter_aws_cdk_demo.api import config
    import cookiecutter_aws_cdk_demo.api as cookiecutter_aws_cdk_demo
"""

from .config import Config
from .config import config
from .cdk import api as cdk
