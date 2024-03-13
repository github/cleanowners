"""Test the functions in the cleanowners module."""

import unittest
import uuid
from unittest.mock import MagicMock, patch

from cleanowners import (
    commit_changes,
    get_repos_iterator,
    get_usernames_from_codeowners,
)


class TestCommitChanges(unittest.TestCase):
    """Test the commit_changes function in cleanowners.py"""

    @patch("uuid.uuid4")
    def test_commit_changes(self, mock_uuid):
        """Test the commit_changes function."""
        mock_uuid.return_value = uuid.UUID(
            "12345678123456781234567812345678"
        )  # Mock UUID generation
        mock_repo = MagicMock()  # Mock repo object
        mock_repo.default_branch = "main"
        mock_repo.ref.return_value.object.sha = "abc123"  # Mock SHA for latest commit
        mock_repo.create_ref.return_value = True
        mock_repo.file_contents.return_value = MagicMock()
        mock_repo.file_contents.update.return_value = True
        mock_repo.create_pull.return_value = "MockPullRequest"

        title = "Test Title"
        body = "Test Body"
        dependabot_file = "testing!"
        branch_name = "codeowners-12345678-1234-5678-1234-567812345678"
        commit_message = "Test commit message"
        result = commit_changes(
            title,
            body,
            mock_repo,
            dependabot_file,
            commit_message,
            "CODEOWNERS",
        )

        # Assert that the methods were called with the correct arguments
        mock_repo.create_ref.assert_called_once_with(
            f"refs/heads/{branch_name}", "abc123"
        )
        mock_repo.file_contents.assert_called_once_with("CODEOWNERS")
        mock_repo.create_pull.assert_called_once_with(
            title=title,
            body=body,
            head=branch_name,
            base="main",
        )

        # Assert that the function returned the expected result
        self.assertEqual(result, "MockPullRequest")


class TestGetUsernamesFromCodeowners(unittest.TestCase):
    """Test the get_usernames_from_codeowners function in cleanowners.py"""

    def test_get_usernames_from_codeowners(self):
        """Test the get_usernames_from_codeowners function."""
        codeowners_file_contents = MagicMock()
        codeowners_file_contents.decoded = """
        # Comment
        @user1
        @user2
        @org/team
        # Another comment
        @user3 @user4
        """.encode(
            "ASCII"
        )
        expected_usernames = ["user1", "user2", "user3", "user4"]

        result = get_usernames_from_codeowners(codeowners_file_contents)

        self.assertEqual(result, expected_usernames)


class TestGetReposIterator(unittest.TestCase):
    """Test the get_repos_iterator function in evergreen.py"""

    @patch("github3.login")
    def test_get_repos_iterator_with_organization(self, mock_github):
        """Test the get_repos_iterator function with an organization"""
        organization = "my_organization"
        repository_list = []
        github_connection = mock_github.return_value

        mock_organization = MagicMock()
        mock_repositories = MagicMock()
        mock_organization.repositories.return_value = mock_repositories
        github_connection.organization.return_value = mock_organization

        result = get_repos_iterator(organization, repository_list, github_connection)

        # Assert that the organization method was called with the correct argument
        github_connection.organization.assert_called_once_with(organization)

        # Assert that the repositories method was called on the organization object
        mock_organization.repositories.assert_called_once()

        # Assert that the function returned the expected result
        self.assertEqual(result, mock_repositories)

    @patch("github3.login")
    def test_get_repos_iterator_with_repository_list(self, mock_github):
        """Test the get_repos_iterator function with a repository list"""
        organization = None
        repository_list = ["org/repo1", "org2/repo2"]
        github_connection = mock_github.return_value

        mock_repository = MagicMock()
        mock_repository_list = [mock_repository, mock_repository]
        github_connection.repository.side_effect = mock_repository_list

        result = get_repos_iterator(organization, repository_list, github_connection)

        # Assert that the repository method was called with the correct arguments for each repository in the list
        expected_calls = [
            unittest.mock.call("org", "repo1"),
            unittest.mock.call("org2", "repo2"),
        ]
        github_connection.repository.assert_has_calls(expected_calls)

        # Assert that the function returned the expected result
        self.assertEqual(result, mock_repository_list)
