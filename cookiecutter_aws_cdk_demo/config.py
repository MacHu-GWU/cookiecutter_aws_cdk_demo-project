# -*- coding: utf-8 -*-

"""
Project configuration shared by every CDK stack.
"""

from __future__ import annotations

import dataclasses

from .paths import PACKAGE_NAME


@dataclasses.dataclass
class Config:
    """
    Project-wide settings. Every name a stack puts into AWS is derived from
    :attr:`project_name`, so stacks of different projects never collide in one account.
    """

    # fmt: off
    project_name: str = dataclasses.field()  #: Project name in snake_case or slug-case, such as ``my_project``.
    # fmt: on

    @property
    def project_name_snake(self) -> str:
        """
        Project name in snake_case, such as ``my_project``.
        """
        return self.project_name.replace("-", "_")

    @property
    def project_name_slug(self) -> str:
        """
        Project name in slug-case, such as ``my-project``.
        """
        return self.project_name_snake.replace("_", "-")

    def get_stack_id(self, short_name: str) -> str:
        """
        Build a stack's construct ID, which is also its CloudFormation stack name
        and the ``<slug>`` of its ``cdk-*-<slug>`` mise tasks.

        :param short_name: what the stack holds, in slug-case, such as ``param``.

        :returns: ``<project_name_slug>-<short_name>``, such as ``my-project-param``.
        """
        return f"{self.project_name_slug}-{short_name}"


config = Config(
    project_name=PACKAGE_NAME,
)
"""
The configuration of this project.
"""
