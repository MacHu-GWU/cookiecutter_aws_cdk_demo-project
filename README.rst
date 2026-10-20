
.. image:: https://readthedocs.org/projects/cookiecutter-aws-cdk-demo/badge/?version=latest
    :target: https://cookiecutter-aws-cdk-demo.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/cookiecutter_aws_cdk_demo-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/cookiecutter_aws_cdk_demo-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/cookiecutter_aws_cdk_demo-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/cookiecutter_aws_cdk_demo-project

.. image:: https://img.shields.io/pypi/v/cookiecutter-aws-cdk-demo.svg
    :target: https://pypi.python.org/pypi/cookiecutter-aws-cdk-demo

.. image:: https://img.shields.io/pypi/l/cookiecutter-aws-cdk-demo.svg
    :target: https://pypi.python.org/pypi/cookiecutter-aws-cdk-demo

.. image:: https://img.shields.io/pypi/pyversions/cookiecutter-aws-cdk-demo.svg
    :target: https://pypi.python.org/pypi/cookiecutter-aws-cdk-demo

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/cookiecutter_aws_cdk_demo-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/cookiecutter_aws_cdk_demo-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://cookiecutter-aws-cdk-demo.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/cookiecutter_aws_cdk_demo-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/cookiecutter_aws_cdk_demo-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/cookiecutter_aws_cdk_demo-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/cookiecutter-aws-cdk-demo#files


Welcome to ``cookiecutter_aws_cdk_demo`` Documentation
==============================================================================
.. image:: https://cookiecutter-aws-cdk-demo.readthedocs.io/en/latest/_static/cookiecutter_aws_cdk_demo-logo.png
    :target: https://cookiecutter-aws-cdk-demo.readthedocs.io/en/latest/

A template for a code base that manages several AWS CDK stacks across several environments (``dev``, ``tst``, ``prd``), built on `cdk_mate <https://github.com/MacHu-GWU/cdk_mate-project>`_. Two sample stacks show the pattern, both free while idle:

- **alerts** (``cdk/stacks/alerts_stack.py``, a simple stack in one file): an SNS topic and an SSM parameter holding the environment's log level.
- **publisher** (``cdk/stacks/publisher_stack/``, the folder form with one mixin per resource group): an IAM role allowed to publish to the alerts topic, and an SSM parameter with the topic ARN. It depends on the alerts stack of the same environment.

Each stack has a ``<name>_stack_exports.py`` that imports nothing from this project, so another project copies that one file to read the stack's outputs. Its ``to_dict()`` lists every value it provides; ``mise run int-test`` checks them against the deployed stack.


Stack Workflow
------------------------------------------------------------------------------
Every (environment, stack) pair gets four mise tasks, ``cdk-<action>-<env>-<stack>-stack``; the ``-stack`` ending marks a task that acts on one stack only. ``cdk-<action>-<env>-all`` runs the action on every stack of the environment, so no stack may be named ``all``:

.. list-table::
    :header-rows: 1

    * - Task
      - What it does
    * - ``cdk-synth-<env>-<stack>-stack``
      - Synthesize the CloudFormation template; no AWS call
    * - ``cdk-plan-<env>-<stack>-stack``
      - Diff against what is deployed, through a CloudFormation change set; deploys nothing
    * - ``cdk-up-<env>-<stack>-stack``
      - Deploy, without an approval prompt
    * - ``cdk-down-<env>-<stack>-stack``
      - Destroy, without confirmation

Each task is one plain cdk command, run in ``cdk/`` with ``ENV_NAME=<env>`` set, such as ``cdk deploy cookiecutter-aws-cdk-demo-prd-alerts --exclusively --require-approval never --profile {{env.AWS_PROFILE_FOR_PRD}}``. A single stack is selected by its construct ID (its stack name) with ``--exclusively``; ``all`` lets the cdk CLI order the stacks by their dependencies. ``synth`` makes no AWS call and takes no profile; the other actions stop with an error if the profile variable is not set. Before the cdk command, a task prints the CloudFormation console URL of each stack it acts on (one for a ``-stack`` task, all of them for an ``all`` task) and the command line.

Setup: copy ``.env.example`` to ``.env`` and set ``AWS_PROFILE_FOR_DEV``, ``AWS_PROFILE_FOR_TST`` and ``AWS_PROFILE_FOR_PRD``; mise loads it for every task. An environment without one falls back to the default credential chain. ``ENV_NAME`` in ``.env`` sets the current environment for everything else (default ``dev``). Every stack is bound to the ``aws_account_id`` and ``aws_region`` of its config, so the cdk CLI refuses to deploy it with the credentials of another account. Then, for example:

.. code-block:: bash

    mise run cdk-plan-dev-alerts-stack
    mise run cdk-up-dev-all

``mise run print-cdk-stack-urls`` prints the console URL of every stack in every environment, without calling AWS. An environment whose config cannot load, such as one without its ``-secret`` file, prints an error line instead, and the others are still printed.

Config lives in ``config/*.json5`` (json5 allows comments). ``Config.load_from_local_config_file`` merges, in order, ``config-shared.json5``, ``config-shared-secret.json5``, ``config-<env>.json5`` and ``config-<env>-secret.json5``, a later file overriding the keys of an earlier one. The ``-secret`` files are git-ignored and optional; ``config/example/`` shows the shape of each file. Deploys run only from a local machine: ``Config.load`` refuses any other runtime.

How the code is organized: everything environment specific is a lazy property of ``one`` and belongs to the **current environment**, ``one.env.current_env_name``, which the ``ENV_NAME`` environment variable selects (default ``dev``):

.. list-table::
    :header-rows: 1

    * - ``one.<name>``
      - What it is
      - Module
    * - ``config``
      - the ``Config`` of the current environment
      - ``config/config_00_main.py``
    * - ``bsm``
      - its boto session: locally the profile ``AWS_PROFILE_FOR_<ENV>`` when set, otherwise the default credential chain
      - ``one/one_02_boto_ses.py``
    * - ``stack_ctx_enum``
      - one ``cdk_mate.StackCtx`` per stack, with names, account, region and session; what ``mise run cdk-gen-tasks`` and Python scripts use
      - ``cdk/stack_ctx_enum.py``
    * - ``stack_enum``
      - one CDK stack per stack, created in one ``cdk.App``; what ``cdk/cdk_app.py`` synthesizes
      - ``cdk/stack_enum.py``

Tests: ``mise run cov`` runs the unit tests in ``tests/``, with no AWS call; for a stack that is just a synth smoke test through ``StackEnum``. ``mise run int-test`` runs ``tests_int/`` against the stacks deployed in ``ENV_NAME``, such as loading each ``*_stack_exports.py`` and calling ``to_dict()``, which fails if an output is missing; those modules are left out of coverage.

So the cdk app only holds the stacks of one environment, each with its stack name as construct ID, such as ``cookiecutter-aws-cdk-demo-prd-alerts``. The cdk CLI passes ``ENV_NAME`` on to the app, so ``ENV_NAME=prd cdk synth`` synthesizes prd, and deploying dev does not need the prd config.

To add a stack:

1. In ``cookiecutter_aws_cdk_demo/config/config_01_name.py``, add ``cft_stack_name_<x>`` / ``cft_stack_url_<x>`` and the names of the resources the stack holds. Names are built only there.
2. Write the stack in ``cookiecutter_aws_cdk_demo/cdk/stacks/``: ``<x>_stack.py``, or ``<x>_stack/stack.py`` plus ``stack_0N_<topic>.py`` mixins once it grows. It takes ``(scope, id, stack_name, env, config)`` plus the resources of other stacks it uses.
3. Add a ``<x>`` entry to ``StackCtxEnum`` and ``StackEnum``, after the stacks it depends on.
4. If other projects need its outputs, add ``<x>_stack_exports.py`` (stdlib only, literal stack names, every value listed in ``to_dict``) and a ``tests_int/`` test that loads it and calls ``to_dict``.
5. Run ``mise run cdk-gen-tasks``. It rewrites the block between ``# <cdk-stack-tasks>`` and ``# </cdk-stack-tasks>`` in ``mise.toml``; never edit that block by hand. A unit test fails while the block is out of date.


.. _install:

Install
------------------------------------------------------------------------------

``cookiecutter_aws_cdk_demo`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install cookiecutter-aws-cdk-demo

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade cookiecutter-aws-cdk-demo
