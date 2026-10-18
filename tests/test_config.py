# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.config import Config
from cookiecutter_aws_cdk_demo.config import config

import pytest


class TestConfig:
    @pytest.mark.parametrize(
        "project_name",
        [
            "my_project",
            "my-project",
        ],
    )
    def test_names(self, project_name: str):
        conf = Config(project_name=project_name)
        assert conf.project_name_snake == "my_project"
        assert conf.project_name_slug == "my-project"
        assert conf.get_stack_id("param") == "my-project-param"

    def test_config(self):
        assert config.project_name == "cookiecutter_aws_cdk_demo"


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.config",
        preview=False,
    )
