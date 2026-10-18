# -*- coding: utf-8 -*-

"""
The top-level configuration model.

:class:`Config` holds every project-level setting the stacks and scripts need.
Every name the project puts into AWS is derived from :attr:`Config.project_name`,
so change it once and every stack ID, CloudFormation stack name, and resource
name follows.

To add a group of related settings, put them in a new numbered module
(``config_01_xxx.py``, ``config_02_xxx.py``, ...) as a mixin or a nested model,
then add it to :class:`Config` here. The number gives the reading order: lower
modules are more foundational.

**Where the values come from:** ``config/*.json5`` files at the repo root, read by
:meth:`Config.load_from_local_config_file`. This is an infrastructure project, so the
project admin deploys from a local machine, and :meth:`Config.load` supports no other
runtime on purpose.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import json5

from ..paths import path_enum
from ..runtime import RuntimeNameEnum


@dataclasses.dataclass
class Config:
    """
    Project-wide settings. Every name a stack puts into AWS is derived from
    :attr:`project_name`, so stacks of different projects never collide in one account.
    """

    # fmt: off
    project_name: str = dataclasses.field()  #: Project name in snake_case or slug-case, such as ``my_project``.
    env_name: str = dataclasses.field()  #: The environment these values are for, such as ``dev``.
    hello_value: str = dataclasses.field()  #: Value of the sample SSM parameter.
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

    @classmethod
    def load_from_local_config_file(
        cls,
        env_name: str,
        dir_config: Path = path_enum.dir_config,
    ) -> Config:
        """
        Load the config of one environment from the json5 files in ``dir_config``.

        Four files are merged, a later one overriding the keys of an earlier one:
        ``config-shared.json5``, ``config-shared-secret.json5``,
        ``config-<env_name>.json5``, ``config-<env_name>-secret.json5``.
        The ``-secret`` files are git-ignored and may be missing; the others are required.
        ``config/example/`` shows the shape of every file.

        :param env_name: such as ``dev``, see :class:`~cookiecutter_aws_cdk_demo.env.EnvNameEnum`.
        :param dir_config: the folder of the config files.
        """
        data = {}
        for name in ["shared", env_name]:
            path = dir_config / f"config-{name}.json5"
            data.update(json5.loads(path.read_text(encoding="utf-8")))
            path_secret = dir_config / f"config-{name}-secret.json5"
            if path_secret.exists():
                data.update(json5.loads(path_secret.read_text(encoding="utf-8")))
        data["env_name"] = env_name
        return cls(**data)

    @classmethod
    def load(
        cls,
        env_name: str,
        runtime_name: str,
    ) -> Config:
        """
        Load the config the way the current runtime supports.

        :param env_name: such as ``dev``.
        :param runtime_name: such as ``local``, see :class:`~cookiecutter_aws_cdk_demo.runtime.RuntimeNameEnum`.

        :raises NotImplementedError: on any runtime but local; deploy from a local machine.
        """
        if runtime_name == RuntimeNameEnum.local.value:
            return cls.load_from_local_config_file(env_name=env_name)
        else:
            raise NotImplementedError(
                f"loading config on runtime {runtime_name!r} is not supported, "
                "deploy from a local machine"
            )
