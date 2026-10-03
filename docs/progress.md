# Progress

Runs that failed, were skipped or are blocked are recorded here rather than dropped (see `CONTRIBUTING.md`).

## Blocked

- **Second-family experiments and new-domain guard comparison (`results/guru-4500/`)**, 2026-10-01. Not run.
  The configs are ready: `experiments/second_family/matrix.json` and `matrix_timing.json` (the main and timing
  matrices with `internvl3.5-8b` as executor) and `experiments/domains/` (60 scenarios each for files, tickets,
  calendar and chat, change at step 0, the main matrix's eight guards, UI-TARS executor). `stalerun` now builds
  on Windows, so jobs can run on the Ada next to Chrome. What blocks them is memory: in fp8 with an 8192-token
  context, vLLM 0.30.0 could not fit Qwen3-VL-8B in 0.45, 0.48 or 0.5 of the card ("Available KV cache memory:
  -1.04 GiB" at 0.48, after 9.9 GiB of weights), so a planner and an executor cannot share the 24 GB card as
  `scripts/ada/pair.sh` assumes. Options: serve the planner from another machine (a lab 4090 through
  `scripts/lab/tunnel.sh`), or use a smaller planner, which would change the comparison with the main results.
  Port 8000 on the Ada was also held by another project's vLLM server; it was left running.

## Discarded or partial runs

- **Pilot, first attempt**, 2026-10-01 16:36–16:39 on worker-1 and worker-2. The planner server on worker-2 died
  at 16:39, with no error in its log, at the same moment as another team's job on that card. All 42 jobs then used
  up their three attempts within seconds. 5 episodes had finished. Fixed in `openai_compat.py`: model calls now
  retry for up to 15 minutes while a server or tunnel is down.
- **Pilot, second attempt** (`runs/pilot_invalid_v1` on worker-1, 116 episodes), discarded. Two problems made those
  episodes unusable:
  - The shop showed a Filters and Sort sidebar that did nothing, and the agent clicked it until it ran out of steps.
  - `replan_every_step` erased the executor's action history even when the planner handed back the same subtask.
  Both are fixed (`fix: remove dead shop filter controls`, `fix: keep history on unchanged replans`).
- **Pilot, shop tasks on a relative criterion** (`results/vivian-4090/pilot`, shop cheapest and highest rated rows).
  Kept, but they don't measure staleness. The results bar still read "sorted by relevance", the planner kept
  asking to sort, and the executor searched for a sort control that does not exist. Rerun as `pilot_shop_rerun`
  after `fix: drop sort wording from shop results`. Use those rows for shop relative tasks instead.
- **New-domain run, partial** (`results/vivian-4090/domains_lab`, 2 October). The run started at 04:56. At 05:40
  another team started `multisports` jobs on both lab 4090s from the shared account. In the same minute our
  executor server on worker-1 stopped with no error in its log, and `~/capstone_pilots/venvq`, the Python
  environment the planner server ran from, was removed from worker-2. From then on every job failed after its
  15-minute retry window. 19 jobs finished. The episodes that were scored before 05:40 are complete and kept; the
  rest were not run. The campaign scripts on both boxes were stopped at 08:25 by their own process IDs. With the
  other team's jobs on the cards, worker-2 had too little free memory for the planner, so the run can't resume
  until the GPUs free up: reset the failed jobs in `runs/domains_lab.db` and run it again. The monitoring
  heartbeat at 02:00 was not followed up overnight, so the failure went unnoticed until 08:22.
- **Flat reference** moved out of the campaign and ran alone on worker-1 from 08:24, since it needs only the
  executor, which still fit next to the other team's job.
- **fp8 precision control, dropped** (2 October). It was planned because Guru's Ada needed fp8 to hold a planner
  and an executor. Since 2 October every GPU run is on the lab 4090s in bf16, so no result depends on fp8 and the
  control would measure nothing we use. The Ada matrices moved: `experiments/second_family/flat.json` (InternVL
  flat run) and `experiments/small_planner/matrix.json` (now bf16).

## Parser change for the second family (2 October)

A smoke test of InternVL3.5-8B as executor (worker-1, three requests on one inbox screenshot) gave actions like
`click(start_box='Spam[[23, 453, 150, 490]])`: the element's name, then its box on the 0-1000 grid, and no closing
quote. The UI-TARS parser rejected all three, so a flat InternVL run would have measured the parser, not the model.
The coordinates themselves pointed at the right elements. `fix: parse labelled boxes from InternVL` now reads an
unclosed argument and takes coordinates from the last bracketed group. Replaying every action logged in the
finished runs through the new parser gave the same action for all of them, and UI-TARS had no parse failures in
those runs, so no earlier result changes. Parse failures stay part of the InternVL gate.

## Known confounds

- **Executor click loops** (main runs, all guards). Most no-commit episodes end at the step limit with the executor
  clicking one spot (`results/vivian-4090/loops_report.md`). The usual case: the planner says "click the Reply
  button", the click works, and the compose view then shows a bold "Reply" or "Forward" label close to where the
  button was. The executor keeps clicking the label. The screen doesn't change, so it never reports the subtask
  finished and the planner is never asked again. Replaying one such episode in Chrome confirmed that each click on
  the label leaves the screenshot byte-identical. The same pattern shows up on an email or product that is already
  open, and after Add to cart.
  This affects every guard on the same scenarios, so the paired guard comparisons stay valid. But it lowers success
  for all of them, and `replan_every_step` escapes most of these loops simply because it asks the planner at every
  step. Part of its lead may therefore come from breaking loops rather than catching stale subtasks. The
  stall-return ablation (`experiments/main/matrix_stall.json`, architecture `hierarchical_stall`) tests this. There
  the executor hands control back after two actions in a row that leave the screen unchanged, with no change to the
  apps or scenarios, so it pairs with `main` scenario by scenario.

## Plan changes on the night of 1 October

- The main comparison took about four hours, and the queue behind it would not have finished by 07:00. To fit,
  `delegated` dropped `self_check` (the costliest guard and a weak one in main) and `domains_lab` dropped
  `dom_subtask_replan` (`rebind_dom` reads the same DOM signal with fewer false alarms). The stall-return ablation
  was added after the timing study. Order: timing, main_stall, delegated, domains_lab, flat.
- Code is promoted on worker-1 only between matrices. `main` ran commit `3c5edae`, `timing` ran `b019e4e`, and
  `main_stall` and later matrices run `210dd66`, as each run's `config.json` records. Between them, `src/` gained
  report code, serving provenance and the `hierarchical_stall` architecture, and `apps/` did not change, so the
  other architectures behave the same in every matrix. Every run is marked dirty because `results/` is not synced
  to the lab boxes.

## The lab runs of 2 October

- Both lab GPUs came back after a reboot on the afternoon of 2 October. From then on Codex launched and watched the
  runs; `scripts/lab/campaign.sh` runs matrices back to back on worker-1, and `scripts/lab/planner_swap.sh` on
  worker-2 swaps the planner when a matrix finishes (worker-1 cannot ssh to worker-2). Both servers ran with batches
  of up to 16 and worker-1 ran 24 jobs at a time (earlier runs: batches of 4, 12 jobs). Batching changes floating-point
  rounding but not which guard sees which scenario, so paired comparisons within a matrix are unaffected; the
  small-planner rows paired against `main` cross this change.
- InternVL3.5-8B failed the action-format gate (`flat_internvl`), so the second-family matrices were dropped.
- The eight-guard domain run supersedes the partial `domains_lab`. Files and tickets sit at the floor under every
  guard, so only calendar separates the guards; the cause (task design or the agent) is not yet known.
- Run code: `domains`, `small_planner` and `flat_internvl` ran commit `0704d26`/`3c35f79` (identical `src/` and
  `apps/`); the launch scripts changed between them.

## Why files and tickets floor under every guard (3 October)

Guru's analysis task (`experiments/analysis/domain_floor.py report results/vivian-4090/domains`). The cause is one
step upstream of the guards, so it is the same for all eight. Files and tickets commit only through a value typed
into an empty field (a share recipient, a ticket assignee), and the executor almost never types: across 480 files
episodes it emitted no `type` action at all, and across 480 tickets episodes only 59. It reaches the form and then
clicks the empty field until the step budget runs out: files episodes end at the share dialog (210) or the open file
(209), with 50 ending in `share_refused` from pressing Send on an empty box; 100% of files and ~98% of tickets
episodes hit the step limit. Open and Share both work, so the earlier single trace ("the executor clicks the file and
it never opens") was not representative; the wall is one step later, at text entry.

Calendar is the one domain that separates the guards because its task commits by clicking Join, with no typed value
(0 `type` actions in 480 episodes, 90% under re-plan-every-step). Inbox and shop succeed for the same reason: the
reply body is pre-filled (`setBody` fires on its own) and add-to-cart is a click, so the main runs need almost no
typing either (51 `type` actions in 1640 episodes). So the new-domain run currently measures whether the executor can
fill a text form at all, not whether a guard catches a stale subtask; the guards cannot differ when every episode
fails at the same executor step before any guard decision changes the outcome.

Before files and tickets can say anything about guards, the executor has to get through text entry: either focus the
field when the form opens and show a visible caret, so a click changes the screenshot and the executor stops looping
and types, or make the commit reachable by clicking (a recipient picker, assignee buttons) as calendar is. That is an
apps change (Vivian's half, the `window.stalehand` contract is untouched); the domains matrix would then be rerun.
