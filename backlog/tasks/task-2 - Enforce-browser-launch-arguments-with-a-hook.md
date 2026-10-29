---
id: TASK-2
title: Enforce browser launch arguments with a hook
status: To Do
assignee: []
created_date: '2026-10-29 18:56'
labels:
  - safety
dependencies: []
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The profile path and headless flag reach spawn_browser only through the prompt. Add a can_use_tool / PreToolUse check that rejects spawn_browser calls whose user_data_dir differs from settings, and navigate calls to hosts outside the source's domain.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 spawn_browser with a different profile is denied
- [ ] #2 navigation off the source domain is denied
<!-- AC:END -->
