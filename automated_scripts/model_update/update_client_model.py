import os
import subprocess
import argparse
from github import Github

# ----------------------------
# Git related functions
# ----------------------------

def clone_repo(repo_url, clone_dir):
    """Clone the repo into the given directory."""
    subprocess.run(["git", "clone", repo_url, clone_dir], check=True)


def create_branch(branch_name, repo_dir):
    """Create and switch to a new git branch."""
    subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_dir, check=True)


def make_changes(file_path, content="\n# Automated change"):
    """Append changes to a file to simulate modification."""
    with open(file_path, "a") as f:
        f.write(content)


def commit_and_push(branch_name, repo_dir, commit_message="Automated commit"):
    """Commit changes and push branch to remote."""
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_dir, check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=repo_dir, check=True)


# ----------------------------
# GitHub API related functions
# ----------------------------

def create_pull_request(token, repo_name, head_branch, base_branch="main", title="Automated PR", body="This PR was created by a script."):
    """Create a pull request on GitHub using PyGithub."""
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.create_pull(
        title=title,
        body=body,
        head=head_branch,
        base=base_branch
    )
    return pr.html_url


# ----------------------------
# Main workflow
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Automate repo changes and create a PR.")
    parser.add_argument("--repo-url", required=True, help="GitHub repository HTTPS URL")
    parser.add_argument("--repo-name", required=True, help="Repo in 'owner/name' format")
    parser.add_argument("--branch", default="auto-change-branch", help="New branch name")
    parser.add_argument("--file", default="README.md", help="File to edit")
    parser.add_argument("--base", default="main", help="Base branch for PR")
    parser.add_argument("--commit-message", default="Automated update", help="Commit message")
    parser.add_argument("--pr-title", default="Automated update PR", help="Pull request title")
    parser.add_argument("--pr-body", default="This PR was automatically created.", help="Pull request body")
    args = parser.parse_args()

    clone_dir = "temp_repo"
    github_token = os.environ.get("GITHUB_TOKEN")

    if not github_token:
        raise ValueError("❌ GITHUB_TOKEN environment variable not set")

    # 1. Clone repo
    clone_repo(args.repo_url, clone_dir)

    # 2. Create new branch
    create_branch(args.branch, clone_dir)

    # 3. Make changes
    file_to_edit = os.path.join(clone_dir, args.file)
    make_changes(file_to_edit, "\nAutomated update from script.\n")

    # 4. Commit & push
    commit_and_push(args.branch, clone_dir, args.commit_message)

    # 5. Raise PR
    pr_url = create_pull_request(
        token=github_token,
        repo_name=args.repo_name,
        head_branch=args.branch,
        base_branch=args.base,
        title=args.pr_title,
        body=args.pr_body
    )

    print(f"✅ Pull Request created: {pr_url}")


if __name__ == "__main__":
    main()

