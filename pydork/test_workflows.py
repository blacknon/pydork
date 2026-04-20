#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class WorkflowFileTestCase(unittest.TestCase):
    def test_build_docker_workflow_is_not_empty(self):
        workflow = (REPO_ROOT / '.github' / 'workflows' / 'build_docker.yml').read_text(encoding='utf-8')

        self.assertIn('name: Build Docker image', workflow)
        self.assertIn('actions/checkout@v4', workflow)
        self.assertIn('docker build --tag pydork-ci:latest .', workflow)

    def test_publish_workflow_is_not_empty(self):
        workflow = (REPO_ROOT / '.github' / 'workflows' / 'publish.yml').read_text(encoding='utf-8')

        self.assertIn('name: Publish package', workflow)
        self.assertIn('actions/setup-python@v5', workflow)
        self.assertIn('pypa/gh-action-pypi-publish@release/v1', workflow)

    def test_scraping_workflow_uses_supported_setup_python(self):
        workflow = (REPO_ROOT / '.github' / 'workflows' / 'test_scraping.yml').read_text(encoding='utf-8')

        self.assertIn('actions/checkout@v4', workflow)
        self.assertIn('actions/setup-python@v5', workflow)
        self.assertNotIn('actions/setup-python@v2', workflow)
