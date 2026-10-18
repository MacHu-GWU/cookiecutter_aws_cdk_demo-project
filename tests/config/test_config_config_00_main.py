# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.config.config_00_main import Config

import pytest


def _make_config(project_name: str) -> Config:
    return Config(project_name=project_name, env_name="dev", hello_value="hi")


class TestConfig:
    @pytest.mark.parametrize(
        "project_name",
        [
            "my_project",
            "my-project",
        ],
    )
    def test_names(self, project_name: str):
        conf = _make_config(project_name)
        assert conf.project_name_snake == "my_project"
        assert conf.project_name_slug == "my-project"
        assert conf.get_stack_id("param") == "my-project-param"

    def test_load_from_local_config_file(self, tmp_path):
        """
        Later files override earlier ones, and a missing secret file is skipped.
        """
        (tmp_path / "config-shared.json5").write_text(
            '{project_name: "a", hello_value: "shared"}'
        )
        (tmp_path / "config-dev.json5").write_text("// comment\n{hello_value: 'dev'}")
        (tmp_path / "config-dev-secret.json5").write_text("{project_name: 'b'}")
        conf = Config.load_from_local_config_file(env_name="dev", dir_config=tmp_path)
        assert conf == Config(project_name="b", env_name="dev", hello_value="dev")

    @pytest.mark.parametrize(
        "env_name",
        [
            "dev",
            "tst",
            "prd",
        ],
    )
    def test_load(self, env_name: str):
        """
        The committed config files load for every environment.
        """
        conf = Config.load(env_name=env_name, runtime_name="local")
        assert conf.env_name == env_name

    def test_load_error(self):
        with pytest.raises(NotImplementedError):
            Config.load(env_name="dev", runtime_name="ci")


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.config.config_00_main",
        preview=False,
    )
