# -*- coding: utf-8 -*-

from cookiecutter_aws_cdk_demo.config.config_01_name import ConfigNameMixin

from cookiecutter_aws_cdk_demo.config.api import Config


def test_names(config: Config):
    assert isinstance(config, ConfigNameMixin)
    assert config.project_name_snake == "my_project"
    assert config.project_name_slug == "my-project"
    assert config.prefix_name_slug == "my-project-dev"
    assert config.cft_stack_name_param == "my-project-dev-param"
    assert "filteringText=my-project-dev-param" in config.cft_stack_url_param
    assert config.ssm_param_name_hello == "/my-project-dev/hello"
    assert "/parameters/my-project-dev/hello/" in config.ssm_param_url_hello
    assert config.ssm_param_arn_hello == (
        "arn:aws:ssm:us-east-1:111122223333:parameter/my-project-dev/hello"
    )


if __name__ == "__main__":
    from cookiecutter_aws_cdk_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_cdk_demo.config.config_01_name",
        preview=False,
    )
