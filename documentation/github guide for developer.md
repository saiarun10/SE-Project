# Developer Github Workflow Guide

This document outlines the GitHub workflow for contributing to a repository owned by another user. It covers cloning, branching, committing, pushing, creating pull requests, and managing branches for a project with `backend`, `frontend`, and `test` directories in the `main` branch. For initial project setup, refer to `Project Setup Guide.md`.

## Table of Contents

- [Requesting Contributor Access](#requesting-contributor-access)
- [Cloning the Repository](#cloning-the-repository)
- [Creating a Branch](#creating-a-branch)
- [Committing and Pushing Changes](#committing-and-pushing-changes)
- [Creating Pull Requests](#creating-pull-requests)
- [Resolving Merge Conflicts](#resolving-merge-conflicts)
- [Managing Branches](#managing-branches)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Git Commands Reference](#git-commands-reference)
- [Best Practices](#best-practices)

## Requesting Contributor Access

To contribute to this repository, you must obtain appropriate permissions from the repository owner.

1. **Request Access**:
   - Contact the repository owner to be added as a collaborator via `Settings > Collaborators and teams > Add people`.
   - Accept the invitation sent to your GitHub account.

2. **Verify Permissions**:
   - Ensure you have `Write` access to clone, create branches, and submit pull requests.
   - Confirm your access level in `Settings > Collaborators and teams`.

## Cloning the Repository

Clone the repository to your local environment:

```bash
git clone https://github.com/saiarun10/SE-Project.git
cd SE-Project
```

## Creating a Branch

Isolate your work in a feature branch to avoid conflicts with the `main` branch. Use `git switch` (recommended for Git 2.23+) for its clarity and safety, or `git checkout` for older Git versions.

### Using `git switch` (Recommended)
The `git switch` command is designed for branch operations, reducing the risk of unintended actions (e.g., detaching HEAD) compared to `git checkout`.

```bash
git checkout main
git pull origin main
git switch -c feature/<branch-name>
```

### Using `git checkout` (Alternative)
Use `git checkout` if `git switch` is unavailable:

```bash
git checkout main
git pull origin main
git checkout -b feature/<branch-name>
```

- **Naming Convention**: Use descriptive names with prefixes, e.g., `feature/add-authentication`, `bugfix/ui-alignment`.

## Committing and Pushing Changes

1. **Make Changes**: Edit files in the `backend`, `frontend`, or `test` directories.
2. **Stage and Commit**:
   ```bash
   git add .
   git commit -m "Descriptive message (e.g., Add user authentication endpoint)"
   ```
3. **Push to Remote**:
   ```bash
   git push origin feature/<branch-name>
   ```

## Creating Pull Requests

Submit your changes for review via a pull request (PR) using GitHub or Visual Studio Code.

### On GitHub
1. Navigate to the repository on GitHub and select your branch.
2. Click “Create pull request.”
3. Provide a clear title (e.g., “Implement user authentication endpoint”) and a detailed description.
4. Assign reviewers, add labels, and submit.

### Using Visual Studio Code
Leverage the **GitHub Pull Requests and Issues** extension for an integrated workflow:

1. **Install the Extension**:
   - Open VS Code and navigate to the Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X`).
   - Search for and install “GitHub Pull Requests and Issues.”
   - Authenticate with GitHub as prompted.

2. **Create a Pull Request**:
   - Push your branch: `git push origin feature/<branch-name>`.
   - Open the GitHub Pull Requests view (GitHub icon in the Activity Bar).
   - Click “Create Pull Request” or respond to the notification.
   - Select the base branch (`main`) and head branch (`feature/<branch-name>`).
   - Enter a title, description, and optional reviewers or labels.
   - Click “Create” to submit.

3. **Advantages**:
   - Minimizes context switching by staying within VS Code.
   - Supports PR creation, review, and commenting directly in the editor.
   - Provides access to your full VS Code environment during reviews.

## Resolving Merge Conflicts

If your pull request encounters conflicts:

1. **Update Your Branch**:
   ```bash
   git checkout feature/<branch-name>
   git fetch origin main
   git merge main
   ```
2. **Resolve Conflicts**:
   - Edit conflicting files to resolve differences.
   - Stage resolved files:
     ```bash
     git add <resolved-file>
     git commit -m "Resolve merge conflicts"
     ```
3. **Push Updates**:
   ```bash
   git push origin feature/<branch-name>
   ```

## Managing Branches

Efficient branch management keeps the repository organized.

### Listing Branches
View available branches:
```bash
git branch                    # List local branches (* indicates current)
git branch -a                 # List local and remote-tracking branches
git branch -r                 # List remote-tracking branches
git branch --show-current     # Display current branch name
```

### Renaming Branches
Rename a local branch:
```bash
git branch -m feature/<old-name> feature/<new-name>  # Rename specific branch
git branch -m <new-name>                             # Rename current branch
git branch -M feature/<old-name> feature/<new-name>  # Force rename (use cautiously)
```

To update the remote:
```bash
git push origin -u feature/<new-name>      # Push new branch and set upstream
git push origin --delete feature/<old-name>  # Delete old branch
```

### Deleting Branches
- **Local Branch**:
  ```bash
  git branch -d feature/<branch-name>  # Safe delete (only if merged)
  git branch -D feature/<branch-name>  # Force delete (use cautiously)
  ```
- **Remote Branch**:
  ```bash
  git push origin --delete feature/<branch-name>  # Preferred syntax
  git push origin :feature/<branch-name>          # Alternative syntax
  ```

### Additional Commands
- Switch to the previous branch:
  ```bash
  git switch -  # or git checkout -
  ```
- Create a branch without switching:
  ```bash
  git branch feature/<branch-name> <start-point>  # e.g., git branch bugfix/urgent HEAD~2
  ```

## Troubleshooting Common Issues

- **“Permission denied” (cloning/pushing)**:
  - Verify `Write` access with the repository owner.
- **“fatal: ref not found”**:
  - Check branch/PR names using `git branch -r`.
- **Merge conflicts**:
  - Refer to [Resolving Merge Conflicts](#resolving-merge-conflicts).
- **“Pull request not appearing”**:
  - Ensure the branch is pushed to the correct repository.
- **VS Code PR issues**:
  - Confirm the GitHub Pull Requests extension is installed and authenticated.
  - Verify the branch is pushed to the remote.
- **“Branch already exists” (renaming)**:
  - Use `git branch -M` or delete the existing branch.

## Git Commands Reference

A comprehensive reference for Git commands used in this workflow:

- **Repository Setup**:
  ```bash
  git init                         # Initialize a new repository
  git clone <url>                  # Clone a repository
  ```

- **Status and Changes**:
  ```bash
  git status                       # Show working directory status
  git diff                         # Show unstaged changes
  git diff --staged                # Show staged changes
  git diff HEAD~1 HEAD             # Compare last two commits
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
  git branch <name>                # Create a branch
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

- **Remote Operations**:
  ```bash
  git remote -v                    # List remotes
  git fetch <remote>               # Fetch updates
  git pull <remote> <branch>       # Fetch and merge
  git push <remote> <branch>       # Push to remote
  git push -u <remote> <branch>    # Push and set upstream
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
  git clean -df                    # Remove untracked files
  ```

## Best Practices

- **Commits**:
  - Create small, focused commits with clear messages (e.g., “feat: Add user login endpoint”).
- **Branching**:
  - Prefer `git switch` for branch operations.
  - Use prefixes (`feature/`, `bugfix/`) for branch names.
  - Delete merged branches to maintain a clean repository.
- **Synchronization**:
  - Regularly pull from `main` to minimize conflicts.
- **Pull Requests**:
  - Use VS Code’s GitHub extension for efficient PR creation and review.
  - Provide detailed PR descriptions, linking to relevant issues.
  - Respond promptly to reviewer feedback.
- **Testing**:
  - Test changes across `backend`, `frontend`, and `test` directories before pushing.
- **Safety**:
  - Avoid force pushes (`git push --force`) unless necessary.
  - Use safe deletion (`git branch -d`) over force deletion (`-D`).
  - Stash uncommitted work (`git stash`) before switching branches.