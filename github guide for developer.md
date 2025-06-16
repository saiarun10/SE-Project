# Developer Guide

This README is for developers contributing to a repository owned by another user. It covers GitHub workflows for cloning, branching, pushing, and creating pull requests for a project with `backend`, `frontend`, and `test` folders in the main branch. For project setup, see the main `Project Setup Guide.md`.

## Table of Contents

- [Requesting Contributor Access](#requesting-contributor-access)
- [Cloning the Repository](#cloning-the-repository)
- [Creating a Branch](#creating-a-branch)
- [Making and Pushing Code](#making-and-pushing-code)
- [Creating Pull Requests](#creating-pull-requests)
- [Handling Merge Conflicts](#handling-merge-conflicts)
- [Common Errors and Solutions](#common-issues-and-solutions)
- [Git Commands Reference](#git-commands-reference)
- [Best Practices](#best-practices)

## Requesting Contributor Access

Since the repository is owned by another user, you need permissions to contribute:

1. **Contact the Owner**:
   - Ask the repository owner to add you as a collaborator via `Settings > Collaborators and teams > Add people`.
   - Accept the invitation link sent to your GitHub account.

2. **Required Permissions**:
   - Request `Write` access to clone, create branches, and submit pull requests.
   - Verify access under `Settings > Collaborators and teams`.

## Cloning the Repository

Clone the repository:

```bash
git clone https://github.com/saiarun10/SE-Project.git
cd SE-Project
```

## Creating a Branch

Work in a feature branch:

```bash
git checkout main
git pull origin main
git checkout -b feature/branch-name
```

Use descriptive names (e.g., `feature/add-login-backend`, `bugfix/frontend-ui`).

## Making and Pushing Code

1. Make changes in `backend`, `frontend`, or `test` folders.
2. Stage and commit:
   ```bash
   git add .
   git commit -m "Add specific feature or fix description"
   ```
3. Push to GitHub:
   ```bash
   git push origin feature/branch-name
   ```

## Creating Pull Requests

1. On GitHub, navigate to the repository and select your branch.
2. Click “Create pull request.”
3. Add a clear title (e.g., “Add login endpoint to backend”) and description.
4. Assign reviewers and submit.

## Handling Merge Conflicts

If your pull request has conflicts:

1. Update your branch:
   ```bash
   git checkout feature/branch-name
   git fetch origin main
   git merge main
   ```
5. Resolve conflicts in affected files:
   ```bash
   git add resolved-file
   git commit -m "Resolve merge conflicts"
   ```
6. Push updates:
   ```bash
   git push origin feature/branch-name
   ```

## Common Issues and Solutions

- **“Permission denied” when cloning or pushing**:
  - Ensure you’re a collaborator with `Write` access. Contact the owner if not.
- **“fatal: ref not found”**:
  - Verify branch or pull request names are correct.
- **Merge conflicts**:
  - Follow [Handling Merge Conflicts](#handling-merge-conflicts).
- **“Pull request not appearing”**:
  - Confirm you pushed to the correct branch and repository.

## Git Commands Reference

- View status:
  ```bash
  git status
  ```
- Check remote branches:
  ```bash
  git fetch origin
  git branch -r
  ```
- Delete local branch:
  ```bash
  git branch -d feature/branch-name
  ```
- Rebase for cleaner history:
  ```bash
  git rebase main
  ```

## Best Practices

- Keep commits small and focused.
- Write clear commit messages (e.g., “Fix frontend button alignment”).
- Sync with `main` regularly to avoid conflicts.
- Respond to reviewer feedback promptly.
- Test changes in all relevant folders before pushing.
