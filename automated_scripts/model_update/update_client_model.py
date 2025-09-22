import os
import subprocess
import argparse
from github import Github
from openai import OpenAI

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

def get_changed_files(token, repo_name, pr_number, path_filter="models/"):
    """Return a list of changed files in PR under models folder."""
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))
    return [f.filename for f in pr.get_files() if f.filename.startswith(path_filter)]

# ----------------------------
# OpenAI helper
# ----------------------------

def update_client_models(be_files, repo_dir, client_dir="Sample App/Model"):
    """Update client Codable files using OpenAI based on BE model changes."""
    client = OpenAI()

    updated_files = []

    for be_file in be_files:
        be_path = os.path.join("models", be_file)
        if not os.path.exists(be_path):
            continue

        be_content = open(be_path).read()

        # Derive matching client file name (simple mapping: Foo.swift <-> Foo.swift)
        filename = os.path.basename(be_file).replace(".py", ".swift")  # adjust if BE not python
        client_path = os.path.join(repo_dir, client_dir, filename)

        if not os.path.exists(client_path):
            print(f"⚠️ Skipping {filename}, no matching client file found")
            continue

        client_content = open(client_path).read()

        print(f"🔄 Updating client file: {client_path} based on {be_file}")

        completion = client.chat.completions.create(
            model="gpt-4.1",  # or gpt-5 if available
            messages=[
                {"role": "system", "content": "You are an expert Swift developer. Update Codable structs based on backend models."},
                {"role": "user", "content": f"""
                Here is the new backend model definition:
                
                {be_content}
                
                Here is the current Swift Codable file:
                
                {client_content}
                
                Update the Swift Codable structs so they fully match the backend model. Preserve existing formatting and coding style.
                Only return the updated Swift code, nothing else. Do not add any explanations. If there are multiple files then give me 
                the full content of the updated file. I would use following code to write it to back to disk:
                ```python
                new_code = completion.choices[0].message.content.strip()

                with open(client_path, "w") as f:
                    f.write(new_code)

                updated_files.append(client_path)
                ``` Give the output such that the above code can save the changes correctly.
                """}
            ],
        )

        new_code = completion.choices[0].message.content.strip()

        with open(client_path, "w") as f:
            f.write(new_code)

        updated_files.append(client_path)

    return updated_files



# ----------------------------
# Main workflow
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Automate repo changes and create a PR.")
    parser.add_argument("--repo-url", required=True, help="GitHub repository HTTPS URL")
    parser.add_argument("--repo-name", required=True, help="Repo in 'owner/name' format")
    parser.add_argument("--branch", default="auto-change-branch", help="New branch name")
    parser.add_argument("--base", default="main", help="Base branch for PR")
    parser.add_argument("--commit-message", default="Automated update", help="Commit message")
    parser.add_argument("--pr-title", default="Automated update PR", help="Pull request title")
    parser.add_argument("--pr-body", default="This PR was automatically created.", help="Pull request body")
    parser.add_argument("--pr-number", required=True, help="Backend PR number to fetch changes")

    args = parser.parse_args()

    clone_dir = "temp_repo"
    github_token = os.environ.get("GITHUB_TOKEN")

    if not github_token:
        raise ValueError("❌ GITHUB_TOKEN environment variable not set")

    # 1. Clone repo
    repo_url = "https://" + github_token + "@" + args.repo_url.split("https://")[1]
    clone_repo(repo_url, clone_dir)

    # 2. Create new branch
    create_branch(args.branch, clone_dir)

    # 3. Detect changed BE models
    # changed_files = get_changed_files(github_token, args.repo_name, args.pr_number, "models/")
    # if not changed_files:
    #     print("ℹ️ No backend model changes detected, skipping client updates.")
    #     return

    changed_files = ["UserModel.py"]  # For testing, remove this line in production

    # 4. Update client models
    updated_files = update_client_models(changed_files, clone_dir)

    if not updated_files:
        print("⚠️ No client files updated, aborting.")
        return

    # 5. Commit & push
    commit_and_push(args.branch, clone_dir, args.commit_message)

    # 6. Raise PR
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

