# Module 7: Version Control for Data Engineers

## Why This Module Exists

It's 2 AM. Your pipeline is broken. The dashboard shows wrong numbers. Your boss is asking what happened.

You need to answer:
- What changed?
- When did it change?
- Who changed it?
- Can we go back to when it worked?

**Without version control, you're guessing. With it, you know.**

---

## What "Version Control" Really Means for Data Engineers

In a real company, "version control" isn't just Git. It's a broader concept:

| What Gets Versioned | Why It Matters | Tools |
|---------------------|----------------|-------|
| **Pipeline code** | Track changes to ETL logic | Git |
| **SQL transformations** | Know what query ran when | Git, dbt |
| **Database schemas** | Coordinate schema changes | Flyway, Alembic |
| **Configuration** | Different settings per environment | Git, environment files |
| **Infrastructure** | Reproducible deployments | Terraform, Git |
| **Data itself** | Reproduce historical states | Delta Lake, DVC |

This module focuses on what you'll use **daily as a junior data engineer**: Git for code, plus awareness of the broader ecosystem.

---

## What You'll Learn

| Lesson | Topic | Real-World Application |
|--------|-------|------------------------|
| 1 | Why Version Control Matters | The disasters it prevents |
| 2 | Git Fundamentals | Daily commands you'll use |
| 3 | Branching Strategies | How teams organize work |
| 4 | Collaboration & Code Review | Pull requests, getting feedback |
| 5 | Git for Data Projects | .gitignore, secrets, large files |
| 6 | Database Schema Versioning | Managing schema changes |
| 7 | CI/CD for Data Pipelines | Automated testing & deployment |
| 8 | Data Versioning Concepts | When and why to version data |
| 9 | Environment Management | Dev, staging, production |
| 10 | Putting It Together | Complete workflow walkthrough |

---

## The Reality Check

### What You'll Do Daily
- Commit code changes
- Create branches for new features
- Open pull requests for review
- Review teammates' code
- Resolve merge conflicts

### What You'll Do Weekly
- Deploy changes through CI/CD
- Update configuration files
- Write database migrations

### What You'll Do Occasionally
- Set up new repositories
- Configure CI/CD pipelines
- Investigate historical changes

---

## Industry Context

### How Real Teams Work

**Small startup (2-5 engineers):**
- Simple Git workflow
- Direct commits to main (with review)
- Manual deployments

**Mid-size company (10-50 engineers):**
- Feature branch workflow
- Required code reviews
- CI/CD automation
- Staging environment

**Large enterprise (100+ engineers):**
- Strict branching policies
- Multiple approval requirements
- Automated testing gates
- Separate teams for different pipeline stages

This module prepares you for mid-size company practices, which scale up or down.

---

## Prerequisites

- **Module 1: Linux Basics** - Command line familiarity
- **Module 5: ETL Pipelines** - Understanding what code you're versioning

---

## Exercises

| Exercise | What You'll Build |
|----------|-------------------|
| 1 | Your First Repository | Set up a data project with proper structure |
| 2 | Feature Branch Workflow | Develop a feature using branches |
| 3 | Code Review Simulation | Create and review a pull request |
| 4 | Handling Merge Conflicts | Resolve conflicts in pipeline code |
| 5 | Database Migration | Version a schema change |
| 6 | Complete Project Workflow | End-to-end: branch → develop → review → merge → deploy |

---

## Key Tools

| Tool | Purpose | You'll Learn |
|------|---------|--------------|
| Git | Code version control | Core commands, workflows |
| GitHub/GitLab | Remote hosting, collaboration | PRs, issues, basic Actions |
| Pre-commit | Automated code checks | Setup and configuration |
| Alembic/Flyway | Database migrations | Concepts, basic usage |

---

## What This Module Doesn't Cover (And Why)

- **Advanced Git internals** - You don't need to know how Git stores objects
- **Complex rebasing strategies** - Merge is fine for most data work
- **Full CI/CD pipeline building** - That's DevOps/Platform engineering
- **Data versioning tools in depth** - Covered conceptually; deep dive is advanced

---

## Getting Started

Start with [Lesson 1: Why Version Control Matters](lessons/lesson-01-why-version-control.md)

---

## Quick Reference

After completing this module, use these for quick lookups:

- [Git Commands Cheat Sheet](sample-data/GIT-CHEAT-SHEET.md)
- [.gitignore Template](sample-data/gitignore-template.txt)
- [PR Template](sample-data/pull-request-template.md)
