"""Unit tests for the write_to_markdown function in markdown_writer.py"""

import unittest
from unittest.mock import call, mock_open, patch

from markdown_writer import write_to_markdown


class TestWriteToMarkdown(unittest.TestCase):
    """Test the write_to_markdown function"""

    def test_write_with_all_counts_and_no_users_to_remove(self):
        """Test that the function writes the correct markdown when there are no users to remove"""
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            write_to_markdown(0, 0, 2, 3, {}, [])
            mock_file().write.assert_called_once_with(
                "# Cleanowners Report\n\n"
                "## Overall Stats\n"
                "0 Users to Remove\n"
                "0 Pull Requests created\n"
                "2 Repositories missing or empty CODEOWNERS files\n"
                "3 Repositories with CODEOWNERS file\n"
            )

    def test_write_with_repos_and_users_with_users_to_remove(self):
        """Test that the function writes the correct markdown when there are users to remove"""
        mock_file = mock_open()
        repo_users = {"repo1": ["user1", "user2"], "repo2": ["user3"]}
        with patch("builtins.open", mock_file):
            write_to_markdown(1, 2, 3, 4, repo_users, [])
            calls = [
                call(
                    "# Cleanowners Report\n\n"
                    "## Overall Stats\n"
                    "1 Users to Remove\n"
                    "2 Pull Requests created\n"
                    "3 Repositories missing or empty CODEOWNERS files\n"
                    "4 Repositories with CODEOWNERS file\n"
                ),
                call("## Repositories and Users to Remove\n"),
                call("repo1\n"),
                call("- user1\n"),
                call("- user2\n"),
                call("\n"),
                call("repo2\n"),
                call("- user3\n"),
                call("\n"),
            ]
            mock_file().write.assert_has_calls(calls, any_order=False)

    def test_write_with_repos_missing_codeowners(self):
        """Test that the function writes the correct markdown when there are repos missing CODEOWNERS"""
        mock_file = mock_open()
        repos_missing_codeowners = ["repo1", "repo2"]
        with patch("builtins.open", mock_file):
            write_to_markdown(0, 0, 2, 0, {}, repos_missing_codeowners)
            calls = [
                call(
                    "# Cleanowners Report\n\n"
                    "## Overall Stats\n"
                    "0 Users to Remove\n"
                    "0 Pull Requests created\n"
                    "2 Repositories missing or empty CODEOWNERS files\n"
                    "0 Repositories with CODEOWNERS file\n"
                ),
                call("## Repositories Missing or Empty CODEOWNERS\n"),
                call("- repo1\n"),
                call("- repo2\n"),
                call("\n"),
            ]
            mock_file().write.assert_has_calls(calls, any_order=False)

    def test_write_with_empty_inputs(self):
        """Test that the function writes the correct markdown when all inputs are 0"""
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            write_to_markdown(0, 0, 0, 0, {}, [])
            mock_file().write.assert_called_once_with(
                "# Cleanowners Report\n\n"
                "## Overall Stats\n"
                "0 Users to Remove\n"
                "0 Pull Requests created\n"
                "0 Repositories missing or empty CODEOWNERS files\n"
                "0 Repositories with CODEOWNERS file\n"
            )


if __name__ == "__main__":
    unittest.main()
