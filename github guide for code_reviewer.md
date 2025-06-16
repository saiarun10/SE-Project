# Code Reviewer Guide

This README is for code reviewers managing pull requests in a repository owned by another user. It covers GitHub workflows for reviewing and merging code in a project with `backend`, `frontend`, and `test` folders in the main branch. For project setup, refer to the main `Project Setup Guide.md`.

## Table of Contents

- [Becoming a Code Reviewer or Merger](#becoming-a-code-reviewer-or-merger)
- [Cloning the Repository](#cloning-the-repository)
- [Checking Out Pull Requests](#checking-out-pull-requests)
- [Reviewing Code](#reviewing-code)
- [Handling Merge Conflicts](#handling-merge-conflicts)
- [Merging Pull Requests](#merging-pull-requests)
- [Common Errors and Solutions](#common-errors-and-solutions)
- [Git Commands Reference](#git-commands-reference)
- [Best Practices](#best-practices)

## Becoming a Code Reviewer or Merger

Since the repository is owned by another user, you need specific permissions to review or merge pull requests:

1. **Request Access**:
   - Contact the repository owner or an admin to add you as a collaborator.
   - On GitHub, the owner can invite you via `Settings > Collaborators and teams > Add people`. You’ll receive an email invitation to accept.

2. **Required Permissions**:
   - For **code reviewer**: Request at least `Write` access to comment on and approve pull requests.
   - For **merger**: Request `Admin` or `Maintain` access to merge pull requests and manage branches.
   - The owner can assign these roles when adding you as a collaborator or team member.

3. **Verify Access**:
   - After accepting the invitation, check your permissions under `Settings > Collaborators and teams`.
   - Ensure you can create branches, push changes, and merge pull requests (if applicable).

## Cloning the Repository

Clone the repository to start reviewing:

```bash
git clone https://github.com/saiarun10/SE-Project.git
cd SE-Project
```

## Checking Out Pull Requests

To review a pull request locally:

```bash
git fetch origin pull/PR_NUMBER/head:pr-PR_NUMBER
git checkout pr-PR_NUMBER
```

Replace `PR_NUMBER` with the pull request number from GitHub.

## Reviewing Code

- Use GitHub’s web interface or local tools (e.g., `git diff`) to review changes.
- Check code in `backend`, `frontend`, and `test` folders for quality, standards, and functionality.
- Leave feedback via GitHub comments, requesting changes if needed.

## Handling Merge Conflicts

If a pull request has merge conflicts:

1. Switch to the `main` branch:
   ```bash
   git checkout main
   git pull origin main
   ```
2. Switch to the pull request branch:
   ```bash
   git checkout pr-PR_NUMBER
   ```
3. Merge `main` into the pull request branch:
   ```bash
   git merge main
   ```
4. Resolve conflicts in affected files (`backend`, `frontend`, or `test`).
5. Stage and commit resolved files:
   ```bash
   git add resolved-file
   git commit -m "Resolve merge conflicts"
   ```
6. Push the updated branch:
   ```bash
   git push origin pr-PR_NUMBER
   ```

Notify the pull request author to update their branch if you lack push access.

## Merging Pull Requests

With `Maintain` or `Admin` access:

- On GitHub, go to the pull request and click “Merge pull request” after approval.
- Or merge locally:
  ```bash
  git checkout main
  git merge pr-PR_NUMBER
  git push origin main
  ```

If you lack merge permissions, request the owner to merge or escalate your access.

## Common Errors and Solutions

- **“fatal: Couldn't find remote ref pull/PR_NUMBER/head”**:
  - Verify the pull request number and ensure it exists on GitHub.
- **“Permission denied” when pushing**:
  - Confirm you have `Write` or higher access. Contact the owner to upgrade your permissions.
- **Merge conflicts**:
  - Follow [Handling Merge Conflicts](#handling-merge-conflicts). If you can’t push, ask the PR author to resolve.
- **“You are not authorized to merge”**:
  - Request `Maintain` or `Admin` access from the repository owner.

## Git Commands Reference

- Create a new branch:
  ```bash
  git checkout main
  git pull origin main
  git checkout -b feature/branch-name
  ```
- Push a new branch:
  ```bash
  git push origin feature/branch-name
  ```
- Update a branch with main:
  ```bash
  git checkout feature/branch-name
  git merge main
  ```
- View changes:
  ```bash
  git diff main
  ```

## Best Practices

- Provide constructive, specific comments during reviews.
- Ensure changes align with project goals across `backend`, `frontend`, and `test`.
- Verify tests pass before approving.
- Communicate with the owner promptly if permissions are insufficient.
