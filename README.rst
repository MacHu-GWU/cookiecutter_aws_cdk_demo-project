
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

A template for a code base that manages multiple AWS CDK stacks. Every stack gets its own set of mise tasks, and the reserved slug ``all`` runs the same action on every stack. The sample stack holds one SSM parameter, ``/cookiecutter-aws-cdk-demo/hello``, with the value ``hello world``.


Stack Workflow
------------------------------------------------------------------------------
Each stack has five tasks, ``cdk-<action>-<slug>``, where ``<slug>`` is the stack's construct ID (also its CloudFormation stack name), such as ``cookiecutter-aws-cdk-demo-param``:

.. list-table::
    :header-rows: 1

    * - Task
      - What it does
    * - ``cdk-synth-<slug>``
      - Synthesize the CloudFormation template; changes nothing in AWS
    * - ``cdk-plan-<slug>``
      - Diff against what is deployed, through a CloudFormation change set; deploys nothing
    * - ``cdk-up-<slug>``
      - Deploy, without an approval prompt
    * - ``cdk-down-<slug>``
      - Destroy, without confirmation
    * - ``cdk-down-ask-<slug>``
      - Destroy, after a confirmation prompt

``cdk-<action>-all`` runs the action on every stack, so no stack may have the ID ``all``.

Setup: copy ``.env.example`` to ``.env`` and set ``AWS_PROFILE``; mise loads it for every task. Then, for example:

.. code-block:: bash

    mise run cdk-plan-cookiecutter-aws-cdk-demo-param
    mise run cdk-up-all

Config lives in ``config/*.json5`` (json5 allows comments). ``Config.load_from_local_config_file`` merges, in order, ``config-shared.json5``, ``config-shared-secret.json5``, ``config-<env>.json5`` and ``config-<env>-secret.json5``, a later file overriding the keys of an earlier one. The ``-secret`` files are git-ignored and optional; ``config/example/`` shows the shape of each file. Deploys run only from a local machine: ``Config.load`` refuses any other runtime.

To add a stack:

1. Write the stack class in ``cookiecutter_aws_cdk_demo/cdk/stacks/``.
2. Add a ``@cached_property`` that returns it to ``StackEnum`` in ``cookiecutter_aws_cdk_demo/cdk/stack_enum.py``, with the ID from ``self.one.config.get_stack_id("<short_name>")``.
3. Run ``mise run cdk-gen-tasks``. It rewrites the block between ``# <cdk-stack-tasks>`` and ``# </cdk-stack-tasks>`` in ``mise.toml``; never edit that block by hand. A unit test fails while the block is out of date.


.. _install:

Install
------------------------------------------------------------------------------

``cookiecutter_aws_cdk_demo`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install cookiecutter-aws-cdk-demo

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade cookiecutter-aws-cdk-demo
