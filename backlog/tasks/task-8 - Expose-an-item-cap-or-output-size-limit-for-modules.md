---
id: TASK-8
title: Expose an item cap or output-size limit for modules
status: To Do
assignee: []
created_date: '2026-10-29 19:49'
labels:
  - mvp
dependencies: []
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The switch to free-form module output dropped the per-source max_items cap; only max_turns/max_budget_usd and the prompt's 'stop once you have it' bound a visit. Decide whether to reintroduce a size limit (on the dict or in the prompt) after the first live runs.
<!-- SECTION:DESCRIPTION:END -->
