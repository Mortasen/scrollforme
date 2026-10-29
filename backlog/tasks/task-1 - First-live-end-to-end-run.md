---
id: TASK-1
title: First live end-to-end run
status: To Do
assignee: []
created_date: '2026-10-29 18:56'
updated_date: '2026-10-29 18:58'
labels:
  - mvp
dependencies: []
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Log in via 'scrollforme login', run against one Reddit source, and check the agent actually reaches the logged-in feed, stays inside the read-only tools, returns schema-valid JSON and stays within budget. Record real per-source cost and turn counts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 One live run produces a digest.html with real items
- [ ] #2 Observed cost/turns recorded in README defaults
- [ ] #3 A run cut off by max_turns or the budget before close_instance does not leave Chrome holding the profile lock for the next source
<!-- AC:END -->
