# AGENTS.md

## Purpose
This document defines baseline expectations for all contributors to maintain code quality, test coverage, and project stability.

---

## Development Guidelines

### 1. Testing Requirements
- **Always update or create unit tests** for any feature, bug fix, or refactor.  
- Place new tests in the project’s designated test directory or add them to the existing suite.  
- Ensure coverage includes edge cases, not just happy paths.  

### 2. Documentation Requirements
- **Update or create `CHANGELOG.md`** for any notable change.  
  The file should begin with:  
  ```markdown
  # Changelog

  All notable changes to this project will be documented in this file.  
  See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.
  ```
- **Update `README.md`** if changes affect instructions, usage, or accuracy. Do not make trivial edits—only update for correctness or completeness.  
- **Doc Sync:** Always review `README.md`, `CHANGELOG.md`, and other public-facing docs together when making changes to ensure consistency.  

### 3. Local Verification
Before committing changes:
1. Run all tests – confirm full suite passes without errors.  
2. Lint the code – use project linters/formatters.  
3. Fix all linting/formatting issues – use auto-fix where possible, manually handle the rest.  

### 4. Change Workflow
- Make small, reviewable commits.  
- Write clear and descriptive commit messages.  
- Never push untested or lint-failing code.  

### 5. Pull Request Expectations
- PRs must pass all automated checks (tests, linting, builds) before review.  
- Include a short summary of changes and purpose.  
- Reference related issues or tickets where applicable.  

---

## Checklist Before Submitting Code
- [ ] Updated or created unit tests.  
- [ ] All tests pass locally.  
- [ ] Linting run with no errors.  
- [ ] Updated or created `CHANGELOG.md` with notable changes.  
- [ ] Updated `README.md` if information changed or became incomplete.  
- [ ] Verified documentation consistency (`README.md`, `CHANGELOG.md`, public docs).  
- [ ] Commit messages are clear and descriptive.  
- [ ] PR description explains the "why" and "what."  
