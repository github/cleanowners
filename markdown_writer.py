"""Write the results to a markdown file"""


def write_to_markdown(
    users_count,
    pull_count,
    no_codeowners_count,
    codeowners_count,
    repo_and_users_to_remove,
):
    """Write the results to a markdown file"""
    with open("report.md", "w", encoding="utf-8") as file:
        file.write(
            "# Cleanowners Report\n\n"
            "## Overall Stats\n"
            f"{users_count} Users to Remove\n"
            f"{pull_count} Pull Requests created\n"
            f"{no_codeowners_count} Repositories with no CODEOWNERS file\n"
            f"{codeowners_count} Repositories with CODEOWNERS file\n"
        )
        if repo_and_users_to_remove:
            file.write("## Repositories and Users to Remove\n")
            for repo, users in repo_and_users_to_remove.items():
                file.write(f"{repo}\n")
                for user in users:
                    file.write(f"- {user}\n")
                file.write("\n")
