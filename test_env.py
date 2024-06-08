"""Test the get_env_vars function"""

import os
import unittest
from unittest.mock import patch

from env import get_env_vars

BODY = "Consider these updates to the CODEOWNERS file to remove users no longer in this organization."
COMMIT_MESSAGE = "Remove users no longer in this organization from CODEOWNERS file"
ORGANIZATION = "Organization01"
TITLE = "Clean up CODEOWNERS file"
TOKEN = "Token01"


class TestEnv(unittest.TestCase):
    """Test the get_env_vars function"""

    def setUp(self):
        env_keys = [
            "BODY",
            "COMMIT_MESSAGE",
            "DRY_RUN",
            "EXEMPT_REPOS",
            "GH_APP_ID",
            "GH_ENTERPRISE_URL",
            "GH_APP_INSTALLATION_ID",
            "GH_APP_PRIVATE_KEY",
            "GH_TOKEN",
            "ORGANIZATION",
            "REPOSITORY",
            "TITLE",
            "ISSUE_REPORT",
        ]
        for key in env_keys:
            if key in os.environ:
                del os.environ[key]

    @patch.dict(
        os.environ,
        {
            "BODY": BODY,
            "COMMIT_MESSAGE": COMMIT_MESSAGE,
            "DRY_RUN": "false",
            "EXEMPT_REPOS": "repo4,repo5",
            "GH_APP_ID": "",
            "GH_ENTERPRISE_URL": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
            "ORGANIZATION": ORGANIZATION,
            "REPOSITORY": "org/repo1,org2/repo2",
            "TITLE": TITLE,
        },
    )
    def test_get_env_vars_with_org(self):
        """Test that all environment variables are set correctly using an organization"""
        expected_result = (
            ORGANIZATION,
            ["org/repo1", "org2/repo2"],
            None,
            None,
            b"",
            TOKEN,
            "",
            ["repo4", "repo5"],
            False,
            TITLE,
            BODY,
            COMMIT_MESSAGE,
            False,
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "BODY": BODY,
            "COMMIT_MESSAGE": COMMIT_MESSAGE,
            "DRY_RUN": "true",
            "EXEMPT_REPOS": "repo4,repo5",
            "GH_APP_ID": "12345",
            "GH_ENTERPRISE_URL": "",
            "GH_APP_INSTALLATION_ID": "678910",
            "GH_APP_PRIVATE_KEY": "hello",
            "GH_TOKEN": "",
            "ORGANIZATION": "",
            "REPOSITORY": "org/repo1,org2/repo2",
            "TITLE": TITLE,
        },
        clear=True,
    )
    def test_get_env_vars_with_github_app_and_repos(self):
        """Test that all environment variables are set correctly using a list of repositories"""
        expected_result = (
            "",
            ["org/repo1", "org2/repo2"],
            12345,
            678910,
            b"hello",
            "",
            "",
            ["repo4", "repo5"],
            True,
            TITLE,
            BODY,
            COMMIT_MESSAGE,
            False,
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "BODY": BODY,
            "COMMIT_MESSAGE": COMMIT_MESSAGE,
            "DRY_RUN": "true",
            "EXEMPT_REPOS": "repo4,repo5",
            "GH_APP_ID": "",
            "GH_ENTERPRISE_URL": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
            "ORGANIZATION": "",
            "REPOSITORY": "org/repo1,org2/repo2",
            "TITLE": TITLE,
        },
        clear=True,
    )
    def test_get_env_vars_with_token_and_repos(self):
        """Test that all environment variables are set correctly using a list of repositories"""
        expected_result = (
            "",
            ["org/repo1", "org2/repo2"],
            None,
            None,
            b"",
            TOKEN,
            "",
            ["repo4", "repo5"],
            True,
            TITLE,
            BODY,
            COMMIT_MESSAGE,
            False,
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "BODY": BODY,
            "COMMIT_MESSAGE": COMMIT_MESSAGE,
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
            "ORGANIZATION": ORGANIZATION,
            "TITLE": TITLE,
            "ISSUE_REPORT": "true",
        },
    )
    def test_get_env_vars_optional_values(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = (
            ORGANIZATION,
            [],
            None,
            None,
            b"",
            TOKEN,
            "",
            [],
            False,
            TITLE,
            BODY,
            COMMIT_MESSAGE,
            True,
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(os.environ, {})
    def test_get_env_vars_missing_org_or_repo(self):
        """Test that an error is raised if required environment variables are not set"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": ORGANIZATION,
        },
        clear=True,
    )
    def test_get_env_vars_missing_token(self):
        """Test that an error is raised if required environment variables are not set"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
            "ORGANIZATION": ORGANIZATION,
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_no_dry_run(self):
        """Test that all environment variables are set correctly when DRY_RUN is false"""
        expected_result = (
            ORGANIZATION,
            [],
            None,
            None,
            b"",
            TOKEN,
            "",
            [],
            False,
            "Clean up CODEOWNERS file",
            "Consider these updates to the CODEOWNERS file to remove users no longer in this organization.",
            "Remove users no longer in this organization from CODEOWNERS file",
            False,
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
