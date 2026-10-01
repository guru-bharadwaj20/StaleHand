# StaleHand

A test suite for computer-use agents that split work between a planner and an executor. The planner writes a
subtask from one screen; the executor carries it out while the screen keeps changing. StaleHand measures how
often the executor acts on what the planner saw instead of what is on screen now, and compares guards that
prevent it.

Example: asked to "forward the latest email from Samuel Lee", a planner writes "open the email titled Venue
booking for the offsite". A newer email from Samuel Lee arrives. The executor opens the old one.

## Status

Early development. See [docs/design.md](docs/design.md) for the design and [CONTRIBUTING.md](CONTRIBUTING.md)
for the plan.

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev,render,stats]"
.venv/bin/pytest
```
