"""A GitHub Action to suggest removal of non-organization members from CODEOWNERS files."""

import uuid

import auth
import env
import github3


def get_org(github_connection, organization):
    """Get the organization object"""
    try:
        return github_connection.organization(organization)
    except github3.exceptions.NotFoundError:
        print(f"Organization {organization} not found")
        return None


def main():  # pragma: no cover
    """Run the main program"""

    # Get the environment variables
    (
        organization,
        repository_list,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        token,
        ghe,
        exempt_repositories_list,
        dry_run,
        title,
        body,
        commit_message,
    ) = env.get_env_vars()

    # Auth to GitHub.com or GHE
    github_connection = auth.auth_to_github(
        gh_app_id, gh_app_installation_id, gh_app_private_key_bytes, token, ghe
    )
    pull_count = 0
    eligble_for_pr_count = 0
    no_codeowners_count = 0
    codeowners_count = 0
    users_count = 0

    if organization and not repository_list:
        gh_org = get_org(github_connection, organization)
        if not gh_org:
            raise ValueError(
                f"""Organization {organization} is not an organization and
                    REPOSITORY environment variable was not set.
                    Please set valid ORGANIZATION or set REPOSITORY environment
                    variable
                """
            )

    # Get the repositories from the organization or list of repositories
    repos = get_repos_iterator(organization, repository_list, github_connection)

    for repo in repos:
        # Check if the repository is in the exempt_repositories_list
        if repo.full_name in exempt_repositories_list:
            print(f"Skipping {repo.full_name} as it is in the exempt_repositories_list")
            continue

        # Check to see if repository is archived
        if repo.archived:
            print(f"Skipping {repo.full_name} as it is archived")
            continue

        # Check to see if repository has a CODEOWNERS file
        file_changed = False
        codeowners_file_contents = None
        codeowners_filepath = None
        try:
            if repo.file_contents(".github/CODEOWNERS").size > 0:
                codeowners_file_contents = repo.file_contents(".github/CODEOWNERS")
                codeowners_filepath = ".github/CODEOWNERS"
        except github3.exceptions.NotFoundError:
            pass
        try:
            if repo.file_contents("CODEOWNERS").size > 0:
                codeowners_file_contents = repo.file_contents("CODEOWNERS")
                codeowners_filepath = "CODEOWNERS"
        except github3.exceptions.NotFoundError:
            pass
        try:
            if repo.file_contents("docs/CODEOWNERS").size > 0:
                codeowners_file_contents = repo.file_contents("docs/CODEOWNERS")
                codeowners_filepath = "docs/CODEOWNERS"
        except github3.exceptions.NotFoundError:
            pass

        if not codeowners_file_contents:
            print(f"Skipping {repo.full_name} as it does not have a CODEOWNERS file")
            no_codeowners_count += 1
            continue

        codeowners_count += 1

        if codeowners_file_contents.content is None:
            # This is a large file so we need to get the sha and download based off the sha
            codeowners_file_contents = repo.blob(
                repo.file_contents(codeowners_filepath).sha
            ).decode_content()

        # Extract the usernames from the CODEOWNERS file
        usernames = get_usernames_from_codeowners(codeowners_file_contents)

        for username in usernames:
            org = organization if organization else repo.owner.login
            gh_org = get_org(github_connection, org)
            if not gh_org:
                print(f"Owner {org} of repo {repo} is not an organization.")
                break

            # Check to see if the username is a member of the organization
            if not gh_org.is_member(username):
                print(
                    f"\t{username} is not a member of {org}. Suggest removing them from {repo.full_name}"
                )
                users_count += 1
                if not dry_run:
                    # Remove that username from the codeowners_file_contents
                    file_changed = True
                    bytes_username = f"@{username}".encode("ASCII")
                    codeowners_file_contents_new = (
                        codeowners_file_contents.decoded.replace(bytes_username, b"")
                    )

        # Update the CODEOWNERS file if usernames were removed
        if file_changed:
            eligble_for_pr_count += 1
            try:
                pull = commit_changes(
                    title,
                    body,
                    repo,
                    codeowners_file_contents_new,
                    commit_message,
                    codeowners_filepath,
                )
                pull_count += 1
                print(f"\tCreated pull request {pull.html_url}")
            except github3.exceptions.NotFoundError:
                print("\tFailed to create pull request. Check write permissions.")
                continue

    # Report the statistics from this run
    print(f"Found {users_count} users to remove")
    print(f"Created {pull_count} pull requests successfully")
    print(f"Skipped {no_codeowners_count} repositories without a CODEOWNERS file")
    print(f"Processed {codeowners_count} repositories with a CODEOWNERS file")
    if eligble_for_pr_count == 0:
        print("No pull requests were needed")
    else:
        print(
            f"{round((pull_count / eligble_for_pr_count) * 100, 2)}% of eligible repositories had pull requests created"
        )
    if codeowners_count + no_codeowners_count == 0:
        print("No repositories were processed")
    else:
        print(
            f"{round((codeowners_count / (codeowners_count + no_codeowners_count)) * 100, 2)}% of repositories had CODEOWNERS files"
        )


def get_repos_iterator(organization, repository_list, github_connection):
    """Get the repositories from the organization or list of repositories"""
    repos = []
    if organization and not repository_list:
        repos = github_connection.organization(organization).repositories()
    else:
        # Get the repositories from the repository_list
        for full_repo_path in repository_list:
            org = full_repo_path.split("/")[0]
            repo = full_repo_path.split("/")[1]
            repos.append(github_connection.repository(org, repo))

    return repos


def get_usernames_from_codeowners(codeowners_file_contents):
    """Extract the usernames from the CODEOWNERS file"""
    usernames = []
    for line in codeowners_file_contents.decoded.splitlines():
        if line:
            line = line.decode()
            # skip comments
            if line.lstrip().startswith("#"):
                continue
            # skip empty lines
            if not line.strip():
                continue
            # Identify handles
            if "@" in line:
                handles = line.split("@")[1:]
                for handle in handles:
                    handle = handle.split()[0]
                    # Identify team handles by the presence of a slash.
                    # Ignore teams because non-org members cannot be in a team.
                    if "/" not in handle:
                        usernames.append(handle)
    return usernames


def commit_changes(
    title,
    body,
    repo,
    codeowners_file_contents_new,
    commit_message,
    codeowners_filepath,
):
    """Commit the changes to the repo and open a pull reques and return the pull request object"""
    default_branch = repo.default_branch
    # Get latest commit sha from default branch
    default_branch_commit = repo.ref("heads/" + default_branch).object.sha
    front_matter = "refs/heads/"
    branch_name = "codeowners-" + str(uuid.uuid4())
    repo.create_ref(front_matter + branch_name, default_branch_commit)
    repo.file_contents(codeowners_filepath).update(
        message=commit_message,
        content=codeowners_file_contents_new,
        branch=branch_name,
    )

    pull = repo.create_pull(
        title=title, body=body, head=branch_name, base=repo.default_branch
    )
    return pull


if __name__ == "__main__":  # pragma: no cover
    main()
