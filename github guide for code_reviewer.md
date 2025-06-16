# Code Reviewer Github Workflow GGuide

This guide is for code reviewers and mergers managing pull requests in a repository owned by another user. It outlines GitHub workflows for reviewing, testing, and merging code in a project with `backend`, `frontend`, and `test` directories in the `main` branch. For project setup, refer to `Project Setup Guide.md`.

## Table of Contents

- [Becoming a Code Reviewer or Merger](#becoming-a-code-reviewer-or-merger)
- [Cloning the Repository](#cloning-the-repository)
- [Checking Out Pull Requests](#checking-out-pull-requests)
- [Reviewing Code](#reviewing-code)
- [Resolving Merge Conflicts](#resolving-merge-conflicts)
- [Merging Pull Requests](#merging-pull-requests)
- [Managing Branches](#managing-branches)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Git Commands Reference](#git-commands-reference)
- [Best Practices](#best-practices)

## Becoming a Code Reviewer or Merger

To review or merge pull requests, you need specific permissions from the repository owner.

1. **Request Access**:
   - Contact the repository owner to be added as a collaborator via `Settings > Collaborators and teams > Add people`.
   - Accept the invitation sent to your GitHub account.

2. **Required Permissions**:
   - **Code Reviewer**: Requires `Write` access to comment on, approve, or request changes to pull requests.
   - **Merger**: Requires `Maintain` or `Admin` access to merge pull requests and manage branches.
   - Confirm your role with the owner.

3. **Verify Access**:
   - Check your permissions under `Settings > Collaborators and teams`.
   - Ensure you can push changes, approve pull requests, or merge (depending on your role).

## Cloning the Repository

Clone the repository to your local environment for reviewing code:

```bash
git clone https://github.com/saiarun10/SE-Project.git
cd SE-Project
```

## Checking Out Pull Requests

To review a pull request locally:

```bash
git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>
git switch pr-<PR_NUMBER>
```

- Replace `<PR_NUMBER>` with the pull request number from GitHub.
- Use `git switch` for modern Git versions (2.23+) for clarity and safety, or `git checkout pr-<PR_NUMBER>` for older versions.

## Reviewing Code

Evaluate pull requests for quality, functionality, and alignment with project standards.

### On GitHub
1. Navigate to the pull request in the repository.
2. Review changes in the `Files changed` tab, focusing on `backend`, `frontend`, and `test` directories.
3. Add comments, suggest changes, or approve the pull request.
4. Request revisions if necessary, providing specific feedback.

### Using Visual Studio Code
Use the **GitHub Pull Requests and Issues** extension for an integrated review workflow:

1. **Install the Extension**:
   - Open VS Code, go to Extensions (`Ctrl+Shift+X` or `Cmd+Shift+X`), and install “GitHub Pull Requests and Issues.”
   - Authenticate with GitHub as prompted.

2. **Review a Pull Request**:
   - Open the GitHub Pull Requests view (GitHub icon in the Activity Bar).
   - Select the pull request from the list.
   - View diffs, add inline comments, suggest changes, or approve directly in VS Code.
   - Checkout the PR branch locally (see [Checking Out Pull Requests](#checking-out-pull-requests)) for testing.

3. **Advantages**:
   - Stay within VS Code, reducing context switching.
   - Access IntelliSense and other VS Code features during reviews.
   - Streamline commenting and approval processes.

### Review Checklist
- Verify code functionality in `backend`, `frontend`, and `test` directories.
- Ensure adherence to coding standards and project guidelines.
- Confirm tests pass and cover new changes.
- Check for security, performance, or maintainability issues.

## Resolving Merge Conflicts

If a pull request has merge conflicts:

1. **Update the Main Branch**:
   ```bash
   git switch main
   git pull origin main
   ```
2. **Switch to the PR Branch**:
   ```bash
   git switch pr-<PR_NUMBER>
   ```
3. **Merge Main**:
   ```bash
   git merge main
   ```
4. **Resolve Conflicts**:
   - Edit conflicting files in `backend`, `frontend`, or `test` directories.
   - Stage and commit resolved files:
     ```bash
     git add <resolved-file>
     git commit -m "Resolve merge conflicts"
     ```
5. **Push Updates**:
   ```bash
   git push origin pr-<PR_NUMBER>
   ```

- **Note**: If you lack push access, notify the pull request author to resolve conflicts and update their branch.

## Merging Pull Requests

With `Maintain` or `Admin` access, merge approved pull requests.

### On GitHub
1. Navigate to the pull request.
2. Verify approvals and passing tests.
3. Click “Merge pull request” and choose a merge strategy (e.g., merge commit, squash, or rebase).
4. Delete the branch after merging (optional).

### Locally
1. Merge the pull request branch into `main`:
   ```bash
   git switch main
   git merge pr-<PR_NUMBER>
   git push origin main
   ```
2. Delete the remote branch (optional):
   ```bash
   git push origin --delete pr-<PR_NUMBER>
   ```

- **Note**: If you lack merge permissions, request the repository owner to merge or escalate your access.

## Managing Branches

Maintain a clean repository by managing branches associated with pull requests.

### Listing Branches
View available branches:
```bash
git branch                    # List local branches (* indicates current)
git branch -a                 # List local and remote-tracking branches
git branch -r                 # List remote-tracking branches
git branch --show-current     # Display current branch name
```

### Renaming Branches
Rename a local branch (if needed for clarity):
```bash
git branch -m pr-<old-number> pr-<new-number>  # Rename specific branch
git branch -m <new-name>                       # Rename current branch
git branch -M pr-<old-number> pr-<new-number>  # Force rename (use cautiously)
```

Update the remote:
```bash
git push origin -u pr-<new-number>      # Push new branch
git push origin --delete pr-<old-number>  # Delete old branch
```

### Deleting Branches
- **Local Branch**:
  ```bash
  git branch -d pr-<PR_NUMBER>  # Safe delete (only if merged)
  git branch -D pr-<PR_NUMBER>  # Force delete (use cautiously)
  ```
- **Remote Branch**:
  ```bash
  git push origin --delete pr-<PR_NUMBER>  # Preferred syntax
  git push origin :pr-<PR_NUMBER>          # Alternative syntax
  ```

### Additional Commands
- Switch to the previous branch:
  ```bash
  git switch -  # or git checkout -
  ```

## Troubleshooting Common Issues

- **“fatal: Couldn't find remote ref pull/<PR_NUMBER>/head”**:
  - Verify the pull request number and ensure it exists on GitHub.
- **“Permission denied” (pushing/merging)**:
  - Confirm `Write` (for pushing) or `Maintain`/`Admin` (for merging) access. Contact the owner if needed.
- **Merge conflicts**:
  - Follow [Resolving Merge Conflicts](#resolving-merge-conflicts) or ask the PR author to resolve.
- **“You are not authorized to merge”**:
  - Request `Maintain` or `Admin` access from the owner.
- **VS Code review issues**:
  - Ensure the GitHub Pull Requests extension is installed and authenticated.
  - Verify the PR is accessible in the GitHub Pull Requests view.
- **“Branch already exists” (renaming)**:
  - Use `git branch -M` or delete the existing branch.

## Git Commands Reference

A comprehensive list of Git commands for code reviewers:

- **Repository Setup**:
  ```bash
  git clone <url>                  # Clone a repository
  ```

- **Status and Changes**:
  ```bash
  git status                       # Show working directory status
  git diff                         # Show unstaged changes
  git diff main pr-<PR_NUMBER>     # Compare branches
  git diff --staged                # Show staged changes
  ```

- **Staging and Committing**:
  ```bash
  git add <file>                   # Stage a file
  git add .                        # Stage all changes
  git reset <file>                 # Unstage a file
  git commit -m "message"          # Commit changes
  git commit --amend               # Amend last commit
  ```

- **History**:
  ```bash
  git log                          # Show commit history
  git log --oneline                # Concise history
  git log --graph --oneline --all  # Graphical branch view
  ```

- **Branch Management**:
  ```bash
  git branch                       # List local branches
  git branch -a                    # List all branches
  git branch -r                    # List remote-tracking branches
  git switch <name>                # Switch to a branch
  git switch -c <name>             # Create and switch
  git checkout <name>              # Alternative to switch
  git checkout -b <name>           # Alternative to switch -c
  git switch -                     # Switch to previous branch
  git branch -m <old> <new>        # Rename a branch
  git branch -d <name>             # Safe delete
  git branch -D <name>             # Force delete
  git push origin --delete <name>  # Delete remote branch
  ```

- **Pull Requests**:
  ```bash
  git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>  # Fetch PR
  git switch pr-<PR_NUMBER>                              # Switch to PR
  ```

- **Remote Operations**:
  ```bash
  git remote -v                    # List remotes
  git fetch <remote>               # Fetch updates
  git pull <remote> <branch>       # Fetch and merge
  git push <remote> <branch>       # Push to remote
  ```

- **Merging and Rebasing**:
  ```bash
  git merge <branch>               # Merge a branch
  git rebase <base-branch>         # Rebase onto a branch
  ```

- **Undoing Changes**:
  ```bash
  git reset --hard <commit>        # Reset to commit (destructive)
  git revert <commit>              # Undo a commit
  git stash                        # Stash changes
  git stash pop                    # Apply and remove stash
  git stash list                   # List stashes
  ```

## Best Practices

- **Code Reviews**:
  - Provide constructive, specific feedback with actionable suggestions.
  - Verify changes align with project goals across `backend`, `frontend`, and `test`.
  - Use VS Code’s GitHub extension for efficient reviews.
- **Testing**:
  - Ensure tests pass and cover new functionality before approving.
  - Test locally if complex changes require validation.
- **Merging**:
  - Prefer squash or rebase merges for a clean history, unless otherwise specified.
  - Delete merged branches to maintain a tidy repository.
- **Branch Management**:
  - Use `git switch` for safe branch operations.
  - Rename or delete branches as needed to avoid clutter.
- **Communication**:
  - Notify PR authors promptly about requested changes or conflicts.
  - Escalate permission issues to the owner immediately.
- **Safety**:
  - Avoid force pushes or force deletions unless necessary.
  - Stash uncommitted work before switching branches.