"""Test the get_env_vars function"""

import os
import unittest
from unittest.mock import patch

from env import get_env_vars


class TestEnv(unittest.TestCase):
    """Test the get_env_vars function"""

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "DRY_RUN": "False",
            "TITLE": "Title01",
            "BODY": "Body01",
            "COMMIT_MESSAGE": "Commit01",
        },
    )
    def test_get_env_vars_with_org(self):
        """Test that all environment variables are set correctly using an organization"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            ["repo4", "repo5"],
            False,
            "Title01",
            "Body01",
            "Commit01",
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "REPOSITORY": "org/repo1,org2/repo2",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "DRY_RUN": "true",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos(self):
        """Test that all environment variables are set correctly using a list of repositories"""
        expected_result = (
            None,
            ["org/repo1", "org2/repo2"],
            "my_token",
            "",
            ["repo4", "repo5"],
            True,
            "Clean up CODEOWNERS file",
            "Consider these updates to the CODEOWNERS file to remove users no longer in this organization.",
            "Remove users no longer in this organization from CODEOWNERS file",
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
        },
    )
    def test_get_env_vars_optional_values(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            [],
            False,
            "Clean up CODEOWNERS file",
            "Consider these updates to the CODEOWNERS file to remove users no longer in this organization.",
            "Remove users no longer in this organization from CODEOWNERS file",
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)

    @patch.dict(os.environ, {})
    def test_get_env_vars_missing_org_or_repo(self):
        """Test that an error is raised if required environment variables are not set"""
        with self.assertRaises(ValueError):
            get_env_vars()

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
        },
        clear=True,
    )
    def test_get_env_vars_missing_token(self):
        """Test that an error is raised if required environment variables are not set"""
        with self.assertRaises(ValueError):
            get_env_vars()

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "DRY_RUN": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_no_dry_run(self):
        """Test that all environment variables are set correctly when DRY_RUN is false"""
        expected_result = (
            "my_organization",
            [],
            "my_token",
            "",
            [],
            False,
            "Clean up CODEOWNERS file",
            "Consider these updates to the CODEOWNERS file to remove users no longer in this organization.",
            "Remove users no longer in this organization from CODEOWNERS file",
        )
        result = get_env_vars()
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
