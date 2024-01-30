"""
Sets up the environment variables for the action.
"""

import os
from os.path import dirname, join

from dotenv import load_dotenv


def get_env_vars() -> tuple[str | None, list[str], str, str, list[str], bool]:
    """
    Get the environment variables for use in the action.

    Args:
        None

    Returns:
        organization (str): The organization to search for repositories in
        repository_list (list[str]): A list of repositories to search for
        token (str): The GitHub token to use for authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        exempt_repositories_list (list[str]): A list of repositories to exempt from the action
        dry_run (bool): Whether or not to actually open issues/pull requests

    """
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

    token = os.getenv("GH_TOKEN")
    # required env variable
    if not token:
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

    return (
        organization,
        repositories_list,
        token,
        ghe,
        exempt_repositories_list,
        dry_run_bool,
    )
