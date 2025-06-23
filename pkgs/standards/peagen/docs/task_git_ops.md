# Task Git Operations

This document summarises which Peagen tasks interact with Git and why.

## mutate
- Commits the winning `winner.py` after a mutation run.
- Creates a branch under `refs/pea/run/<winner-stem>` for inspection.
- Returns the commit SHA in the task result.

## evolve
- Commits the evolve specification before spawning child mutate tasks.
- Creates branches for each child using `fan_out`, allowing parallel runs.
- Returns the commit SHA where the spec was recorded.

## process
- Commits rendered or copied files for each project when a VCS plugin is configured.
- Pushes the active branch to the origin remote; failures raise an exception.
- Result payload includes the commit SHA.

## analysis and DOE
- Analysis and design-of-experiments tasks also commit produced artifacts when a repository is available.

These Git operations make it possible to trace generated artifacts back to the commit that produced them and inspect intermediate branches.
