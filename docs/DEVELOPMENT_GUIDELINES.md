# SmartLearn.AI Development Guidelines

**Version:** 1.0

**Project:** SmartLearn.AI

---

# Purpose

This document defines the development workflow, coding standards, Git workflow, branching strategy, pull request process, and contribution guidelines for all contributors.

Every team member must follow these guidelines.

---

# Project Structure

```
main
│
develop
│
├── feature/*
├── bugfix/*
├── hotfix/*
├── docs/*
├── refactor/*
└── test/*
```

Development must NEVER happen directly on the `main` branch.

---

# Branching Rules

## Main Branch

- Production-ready code only
- Protected branch
- Direct push is NOT allowed
- Merge only through Pull Request

---

## Develop Branch

- Integration branch
- All completed features are merged here first
- Stable development version

---

## Feature Branch

Branch format:

```
feature/<feature-name>
```

Examples

```
feature/login
feature/student-dashboard
feature/teacher-dashboard
feature/rag-pipeline
feature/file-upload
feature/authentication
```

Each feature branch should contain only one feature.

---

## Bug Fix Branch

```
bugfix/<bug-name>
```

Example

```
bugfix/login-api
bugfix/ui-overflow
```

---

## Hotfix Branch

```
hotfix/<critical-fix>
```

Only used for urgent production fixes.

---

## Documentation Branch

```
docs/<topic>
```

Example

```
docs/readme
docs/api
```

---

## Refactor Branch

```
refactor/<module>
```

Example

```
refactor/auth-service
```

---

# Development Workflow

```
GitHub Issue
        ↓
Assign Developer
        ↓
Create Branch
        ↓
Development
        ↓
Local Testing
        ↓
Commit Changes
        ↓
Push Branch
        ↓
Create Pull Request
        ↓
Code Review
        ↓
Fix Review Comments
        ↓
Merge into develop
```

No developer is allowed to merge directly into `main`.

---

# Before Starting Any Task

Every task must have a GitHub Issue.

Do NOT start development without an assigned issue.

Example

Issue #12

Student Dashboard

Assigned to:
Intern 1

---

# Pull Latest Changes

Before starting work

```
git checkout develop
git pull origin develop
```

Then create your feature branch.

```
git checkout -b feature/student-dashboard
```

---

# Commit Message Convention

Use the following format.

Feature

```
feat: add login API
```

Bug

```
fix: resolve JWT validation issue
```

Documentation

```
docs: update setup guide
```

Refactor

```
refactor: simplify authentication service
```

Testing

```
test: add authentication unit tests
```

Maintenance

```
chore: update dependencies
```

Never use commit messages like

```
update
changes
final
done
abc
test
```

---

# Pull Request Rules

Every Pull Request must include

- Summary
- Related Issue
- Testing Details
- Screenshots (if UI)
- Checklist

Example

```
Fixes #15
```

---

# Code Review Rules

At least one approval is required before merging.

Resolve every review comment.

Never merge your own Pull Request without approval unless approved by the Team Lead.

---

# Coding Standards

## Python

- Follow PEP8
- Use type hints
- Write docstrings
- Avoid duplicated code

---

## React

- Functional Components only
- Use TypeScript
- Use Hooks
- Avoid inline styles
- Keep components small

---

## API

- RESTful naming

Good

```
GET /students
POST /students
GET /students/{id}
```

Bad

```
/getStudent
/createStudent
```

---

# Folder Naming

Use lowercase.

Correct

```
student-dashboard
authentication
```

Wrong

```
StudentDashboard
StudentDashboardNew
```

---

# File Naming

React Components

```
StudentCard.tsx
LoginPage.tsx
```

Utilities

```
auth.ts
helper.ts
```

---

# Environment Variables

Never commit

```
.env
```

Commit only

```
.env.example
```

---

# Secrets

Never commit

- API Keys
- Database Passwords
- JWT Secrets
- OAuth Credentials

Use GitHub Secrets.

---

# Dependency Installation

Never install random packages.

Before adding a dependency

- Check license
- Check maintenance
- Discuss with Team Lead

---

# Documentation

Every feature must include

- Code comments
- README update (if required)
- API documentation (if API changed)

---

# Testing

Before creating a Pull Request

- Application builds successfully
- No console errors
- No failing tests
- API works correctly

---

# Issue Management

Every issue must have

- Title
- Description
- Labels
- Assignee
- Priority

---

# Labels

Examples

```
Frontend
Backend
AI
Database
Authentication
Bug
Feature
Documentation
High Priority
Medium Priority
Low Priority
```

---

# Daily Update

Every developer should update the GitHub Project board.

```
Backlog
↓

Todo
↓

In Progress
↓

Review
↓

Testing
↓

Done
```

---

# Communication

Technical discussions should happen in

- GitHub Issues
- GitHub Discussions
- Pull Requests

Avoid discussing implementation details only through WhatsApp or personal chat.

---

# Do Not

❌ Push directly to main

❌ Push broken code

❌ Skip code review

❌ Merge without testing

❌ Commit secrets

❌ Ignore review comments

❌ Leave unused code

---

# Team Responsibilities

## Team Lead

- Architecture
- Code Review
- Project Planning
- AI Design
- Release Management

---

## Frontend Developer

- React UI
- State Management
- API Integration
- Responsive Design

---

## Backend Developer

- FastAPI
- Database
- Authentication
- API Development

---

# Definition of Done

A task is considered complete only if

- Code is implemented
- Code reviewed
- Tests passed
- Documentation updated
- Pull Request merged
- Issue closed

---

# Branch Protection

Protected branches

```
main
develop
```

Rules

- Direct push disabled
- Pull Request required
- Approval required
- Status checks required

---

# Versioning

Semantic Versioning

```
Major.Minor.Patch
```

Example

```
1.0.0
1.1.0
1.1.1
```

---

# Final Rule

Always prioritize

1. Code Quality
2. Readability
3. Maintainability
4. Documentation
5. Testing

Working software is important, but maintainable software is essential.

---

Happy Coding 🚀
