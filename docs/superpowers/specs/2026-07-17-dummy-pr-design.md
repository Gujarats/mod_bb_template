# Dummy Pull Request Design

## Purpose

Create a deliberately minimal pull request that verifies the repository's pull-request workflow.

## Change

Add one root-level file named `DUMMY_PR.md`. Its complete content will be:

```text
Dummy change for pull request testing.
```

No existing project files, build behavior, or mod configuration will change.

## Pull Request

The change will be committed on a new branch and submitted as a clearly labeled test-only pull request. The PR description will state that the file is disposable and can be reverted or closed after workflow verification.

## Validation

Confirm that the commit contains only `DUMMY_PR.md` and that GitHub reports the pull request as open against `main`.
