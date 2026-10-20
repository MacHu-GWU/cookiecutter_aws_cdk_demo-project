# -*- coding: utf-8 -*-

from ..paths import path_enum
from ..vendor.pytest_cov_helper import run_unit_test as _run_unit_test
from ..vendor.pytest_cov_helper import run_cov_test as _run_cov_test


def run_unit_test(
    script: str,
):
    _run_unit_test(
        script=script,
        root_dir=f"{path_enum.dir_project_root}",
    )


def run_cov_test(
    script: str,
    module: str,
    preview: bool = False,
    is_folder: bool = False,
):
    _run_cov_test(
        script=script,
        module=module,
        root_dir=f"{path_enum.dir_project_root}",
        htmlcov_dir=f"{path_enum.dir_htmlcov}",
        preview=preview,
        is_folder=is_folder,
    )


def check_stack_exports(module, exports_class) -> None:
    """
    Integration check of a ``*_stack_exports.py`` module against the stack
    deployed in the current environment (``ENV_NAME``, ``AWS_PROFILE_FOR_<ENV>``).

    - The module imports only the standard library (plus a type-checking-only
      stub), so another project can copy it as is.
    - Its literal stack name is the one in the config.
    - Every property reads an output that the deployed stack really has; the
      values are not checked.
    """
    import ast
    import inspect

    from ..one.api import one

    tree = ast.parse(inspect.getsource(module))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert node.module.split(".")[0] in ["typing", "mypy_boto3_cloudformation"]
        elif isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name in ["typing", "dataclasses"]

    env_name = one.env.current_env_name
    exports = exports_class.load(cf_client=one.cloudformation_client, env_name=env_name)
    assert exports.stack_name == module.STACK_NAMES[env_name]
    for name, attr in vars(exports_class).items():
        if isinstance(attr, property):
            print(f"{exports.stack_name}: {name} = {getattr(exports, name)}")
