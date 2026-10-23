Seed Repo Release and Version History
==============================================================================
The changelog of this **seed repo** itself. The seed is a runnable project that `cookiecutter-aws_cdk <https://github.com/MacHu-GWU/cookiecutter-aws_cdk>`_ (the template repo) turns into a cookiecutter template, so every change here is a change to what newly generated projects get.

- The seed and the template repo share one version number. The source is ``version`` in this repo's ``pyproject.toml``; the template repo copies it and refuses to publish when the two differ.
- ``release-history.rst`` is template content: the starting changelog of every generated project. It never records the seed's own changes, and is never edited for a seed release.
- This file is excluded from the template. Each template release links to its section here.


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


1.0.0 (2026-10-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First release recorded in this file. The version jumps from ``0.1.1`` to ``1.0.0`` because the seed and the template repo now share one version number (both were ``0.1.1``), and the shared version starts at a new major. Nothing generated projects receive is incompatible with ``0.1.1``. This section describes everything a project generated from this seed gets.

**Features and Improvements**

- **Multi-environment AWS CDK code base in Python:** one repo manages several CDK stacks across the ``dev``, ``tst``, and ``prd`` environments
- **Runtime and environment detection:** ``runtime.py`` tells where the code runs, ``env.py`` which environment it targets
- **Config:** one JSON5 file per environment plus a shared file, git-ignored secret files with ``.example`` templates, loaded into a typed config model from which every AWS resource name derives
- **One singleton:** ``one`` binds the config, the boto session of the current environment (``boto-session-manager``), and the CDK stacks, as the single entry point of the package
- **Stacks as code:** ``StackCtxEnum`` (one cdk_mate stack context per stack) and ``StackEnum`` (one CDK stack per stack), two sample stacks (``alerts_stack`` and the multi-file ``publisher_stack``), and a standard-library-only ``<x>_stack_exports.py`` per stack that another project copies to read the stack's CloudFormation outputs
- **One command per stack:** ``cdk-<synth|plan|up|down>-<env>-<stack>-stack`` and ``-all`` mise tasks, generated from the stack enum into a marked block of ``mise.toml`` by ``mise run cdk-gen-tasks``; each prints the CloudFormation console URL, then runs one plain cdk command. ``mise run print-cdk-stack-urls`` prints the console link of every stack
- **Tests:** unit tests synthesize each stack without calling AWS, the enums and the task generator have their own tests, and integration tests (``tests_int/``, ``mise run int-test``) check the deployed stack exports
- **Tools pinned by mise:** Python, Node.js, the AWS CLI, and the cdk CLI (``npm:aws-cdk``), plus ``.env`` loaded for every task
- **Python tooling:** Python 3.11+ (classifiers 3.11 to 3.14), uv with a committed ``uv.lock`` and exported ``requirements*.txt``, ruff format and lint with a one-imported-name-per-statement check, pytest with coverage, Sphinx docs (furo, docfly, nbsphinx) on Read the Docs, GitHub Actions CI, and Codecov
- **Release:** ``mise run release`` creates the GitHub tag and release; the project is not published to PyPI
- **AI ready:** ``CLAUDE.md`` and Claude Code skills: ``pywf-aws-cdk-base`` (the CDK project conventions, with change recipes, every link pinned to this repo's tag of the template version), ``pypi-cdk_mate``, ``aws-cdk-cli-ref``, and the ``pywf-oss-*`` family for the Python tooling (add module, write test, write doc, changelog, release, audit, fix CI, setup machine and repo, upgrade dependencies, write the PyPI skill, add community skills)

**Miscellaneous**

- The links and the version in ``pywf-aws-cdk-base`` now point to ``1.0.0``
- New ``release-history-seed-repo.rst`` (this file) and the seed-only ``pywf-oss-changelog-seed-repo`` skill that maintains it; both stay out of the template
