# Contributing

## Commits

- One logical change per commit. Tests pass at every commit.
- Subject line only, in the form `<type>: <description>`, with a 4 to 6 word description.
- Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `exp` (experiment results).
- No trailers.
- Commit as each piece lands; do not batch a day's work into one commit.

Good: `feat: add newest-first ordering to resolver`, `exp: add inbox pilot replication results`
Bad: `update code`, `fix stuff`, `wip`

## Tests

- Metrics, statistics and the resolver are written test first: they fail quietly and return plausible numbers.
- Unit tests must not need a GPU or a network. Use the scripted model backend.
- Browser tests are marked `browser` and use the system Chrome through Playwright.

## Results

- Never write a number into a doc or report by hand. Reports read result files.
- Every run directory holds `config.json` with the seed, model revisions and library versions.
- A failed or skipped run is recorded in `docs/progress.md`, not dropped.
