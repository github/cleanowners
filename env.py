"""
Sets up the environment variables for the action.
"""

import os
from os.path import dirname, join

from dotenv import load_dotenv


def get_int_env_var(env_var_name: str) -> int | None:
    """Get an integer environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.

    Returns:
        The value of the environment variable as an integer or None.
    """
    env_var = os.environ.get(env_var_name)
    if env_var is None or not env_var.strip():
        return None
    try:
        return int(env_var)
    except ValueError:
        return None


def get_env_vars(
    test: bool = False,
) -> tuple[
    str | None,
    list[str],
    int | None,
    int | None,
    bytes,
    str | None,
    str,
    list[str],
    bool,
    str,
    str,
    str,
    bool,
]:
    """
    Get the environment variables for use in the action.

    Args:
        test (bool): Whether or not to load the environment variables from a .env file (default: False)

    Returns:
        organization (str | None): The organization to search for repositories in
        repository_list (list[str]): A list of repositories to search for
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for authentication
        token (str | None): The GitHub token to use for authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        exempt_repositories_list (list[str]): A list of repositories to exempt from the action
        dry_run (bool): Whether or not to actually open issues/pull requests
        title (str): The title to use for the pull request
        body (str): The body to use for the pull request
        message (str): Commit message to use
        issue_report (bool): Whether or not to create an issue report with the results

    """
    if not test:
        # Load from .env file if it exists
        dotenv_path = join(dirname(__file__), ".env")
        load_dotenv(dotenv_path)

    organization = os.getenv("ORGANIZATION")
    repositories_str = os.getenv("REPOSITORY")
    # Either organization or repository must be set
    if not organization and not repositories_str:
        raise ValueError(
            "ORGANIZATION and REPOSITORY environment variables were not set. Please set one"
        )

    if repositories_str and repositories_str.find("/") == 0:
        raise ValueError(
            "REPOSITORY environment variable was not set correctly. Please set it to a comma separated list of repositories in the format org/repo"
        )

    # Separate repositories_str into a list based on the comma separator
    repositories_list = []
    if repositories_str:
        repositories_list = [
            repository.strip() for repository in repositories_str.split(",")
        ]

    gh_app_id = get_int_env_var("GH_APP_ID")
    gh_app_private_key_bytes = os.environ.get("GH_APP_PRIVATE_KEY", "").encode("utf8")
    gh_app_installation_id = get_int_env_var("GH_APP_INSTALLATION_ID")

    if gh_app_id and (not gh_app_private_key_bytes or not gh_app_installation_id):
        raise ValueError(
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set"
        )

    token = os.getenv("GH_TOKEN")
    if (
        not gh_app_id
        and not gh_app_private_key_bytes
        and not gh_app_installation_id
        and not token
    ):
        raise ValueError("GH_TOKEN environment variable not set")

    ghe = os.getenv("GH_ENTERPRISE_URL", default="").strip()

    exempt_repos = os.getenv("EXEMPT_REPOS")
    exempt_repositories_list = []
    if exempt_repos:
        exempt_repositories_list = [
            repository.strip() for repository in exempt_repos.split(",")
        ]

    dry_run = os.getenv("DRY_RUN")
    dry_run = dry_run.lower() if dry_run else None
    if dry_run:
        if dry_run not in ("true", "false"):
            raise ValueError("DRY_RUN environment variable not 'true' or 'false'")
        dry_run_bool = dry_run == "true"
    else:
        dry_run_bool = False

    title = os.getenv("TITLE")
    # make sure that title is a string with less than 70 characters
    if title:
        if len(title) > 70:
            raise ValueError(
                "TITLE environment variable is too long. Max 70 characters"
            )
    else:
        title = "Clean up CODEOWNERS file"

    body = os.getenv("BODY")
    # make sure that body is a string with less than 65536 characters
    if body:
        if len(body) > 65536:
            raise ValueError(
                "BODY environment variable is too long. Max 65536 characters"
            )
    else:
        body = "Consider these updates to the CODEOWNERS file to remove users no longer in this organization."

    commit_message = os.getenv("COMMIT_MESSAGE")
    if commit_message:
        if len(commit_message) > 65536:
            raise ValueError(
                "COMMIT_MESSAGE environment variable is too long. Max 65536 characters"
            )
    else:
        commit_message = (
            "Remove users no longer in this organization from CODEOWNERS file"
        )

    issue_report = os.getenv("ISSUE_REPORT")
    issue_report = issue_report.lower() if issue_report else None
    if issue_report:
        if issue_report not in ("true", "false"):
            raise ValueError("ISSUE_REPORT environment variable not 'true' or 'false'")
        issue_report_bool = issue_report == "true"
    else:
        issue_report_bool = False

    return (
        organization,
        repositories_list,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        token,
        ghe,
        exempt_repositories_list,
        dry_run_bool,
        title,
        body,
        commit_message,
        issue_report_bool,
    )
