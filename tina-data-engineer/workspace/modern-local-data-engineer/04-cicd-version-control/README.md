# Module 04: CI/CD & Version Control

## Overview

Learn to version control your data pipelines and automate testing with CI/CD - essential skills for professional data engineering.

## Learning Objectives

By the end of this module, you will:
- Use Git workflow for data engineering projects
- Set up pre-commit hooks for code quality
- Create GitHub Actions for automated testing
- Implement CI/CD for dbt projects

## Why This Matters

```
Without CI/CD                    With CI/CD
─────────────────────────────────────────────────────
"It works on my machine"    →   "It works everywhere"
Manual testing              →   Automated testing
Bugs in production          →   Bugs caught early
No code standards           →   Enforced standards
```

## Your Setup

You already have:
- ✅ Git repository (`bi-portfolio`)
- ✅ GitHub remote (`TinaQi87/bi-portfolio`)
- ✅ GitHub Actions (we just added workflow)
- ✅ Pre-commit config (we just added)

## Lessons

| # | Lesson | Duration |
|---|--------|----------|
| 01 | [Git Workflow for Data Engineering](./lessons/01-git-workflow.md) | 30 min |
| 02 | [Pre-commit Hooks](./lessons/02-pre-commit-hooks.md) | 20 min |
| 03 | [GitHub Actions](./lessons/03-github-actions.md) | 30 min |
| 04 | [dbt CI/CD](./lessons/04-dbt-cicd.md) | 30 min |

## Exercises

| # | Exercise | Skills Practiced |
|---|----------|------------------|
| 01 | [Git Branching Practice](./exercises/ex01-git-branching.md) | Branch, commit, merge |
| 02 | [Set Up Pre-commit](./exercises/ex02-setup-precommit.md) | Install and configure hooks |
| 03 | [Trigger CI Pipeline](./exercises/ex03-trigger-ci.md) | Push and watch Actions run |

## Key Concepts

### Git Workflow for Data Projects

```
main (production)
  │
  ├── feature/add-sales-model
  │     ├── commit: "Add stg_sales model"
  │     ├── commit: "Add fct_sales model"
  │     └── commit: "Add tests"
  │           │
  │           ▼
  │     Pull Request ──▶ CI Runs ──▶ Review ──▶ Merge
  │
  └── main (updated)
```

### CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     CI/CD PIPELINE                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  git push ──▶ GitHub ──▶ Actions Triggered                  │
│                              │                               │
│                    ┌─────────┴─────────┐                    │
│                    ▼                   ▼                    │
│              ┌──────────┐       ┌──────────┐               │
│              │  Lint    │       │  Test    │               │
│              │  - black │       │  - pytest│               │
│              │  - flake8│       │  - dbt   │               │
│              │  - sql   │       │          │               │
│              └────┬─────┘       └────┬─────┘               │
│                   │                  │                      │
│                   └────────┬─────────┘                      │
│                            ▼                                │
│                     ┌──────────┐                           │
│                     │ ✓ Pass   │ ──▶ Ready to Merge        │
│                     │ ✗ Fail   │ ──▶ Fix Issues            │
│                     └──────────┘                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### What Gets Checked

| Check | Tool | What It Does |
|-------|------|--------------|
| Python format | black | Consistent code style |
| Python lint | flake8 | Catch errors, bad practices |
| SQL lint | sqlfluff | SQL style and errors |
| dbt compile | dbt parse | Verify models are valid |

## Quick Start

### 1. Install Pre-commit
```bash
pip install pre-commit
cd /path/to/bi-portfolio
pre-commit install
```

### 2. Test Pre-commit
```bash
# Make a change and commit
git add .
git commit -m "Test pre-commit"
# Hooks will run automatically!
```

### 3. View GitHub Actions
1. Push to GitHub
2. Go to: https://github.com/TinaQi87/bi-portfolio/actions
3. Watch your pipeline run

## Files We Added

```
bi-portfolio/
├── .github/
│   └── workflows/
│       └── data-pipeline-ci.yml    ← CI/CD workflow
├── .pre-commit-config.yaml          ← Local hooks
```

## Success Criteria

Before moving to Capstone, ensure you can:
- [ ] Create a feature branch
- [ ] Make commits with good messages
- [ ] Run pre-commit hooks locally
- [ ] Push and see GitHub Actions run
- [ ] Create a Pull Request
- [ ] Merge after CI passes

## Common Issues

### Pre-commit fails on first run
```bash
# Install hooks first
pre-commit install
# Run on all files once
pre-commit run --all-files
```

### GitHub Actions not running
- Check workflow file syntax
- Ensure paths match your changes
- Check Actions tab for errors

## Next Module

Once you complete all exercises, proceed to:
👉 [Module 05: Capstone Pipeline](../05-capstone-pipeline/README.md)
