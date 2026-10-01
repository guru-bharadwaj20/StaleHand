# Model-free checks

## Oracle audit

An oracle that reads item positions from the page performs each scenario's committing flow on the correct target and on the stale one, under the after_handoff timing. A scenario passes when the scorer calls the first a success and the second stale (or the target is gone when the data says it should be).

| domain | scenarios | pass |
|---|---|---|
| calendar | 120 | 100% |
| chat | 120 | 100% |
| files | 120 | 100% |
| inbox | 100 | 100% |
| shop | 210 | 100% |
| tickets | 120 | 100% |
| all | 790 | 100% |

## Click hazard (mid-step change)

A click aimed at the planner's target from the screenshot lands after the change. Columns say what the click opened: the intended item, the item that is now correct, another item, or nothing.

| domain | change | n | intended | now_correct | other_item | nothing |
|---|---|---|---|---|---|---|
| calendar | irrelevant | 40 | 0% | 0% | 100% | 0% |
| calendar | none | 40 | 50% | 0% | 50% | 0% |
| calendar | relevant | 30 | 0% | 10% | 90% | 0% |
| calendar | target_removed | 10 | 0% | 0% | 100% | 0% |
| chat | irrelevant | 50 | 20% | 0% | 80% | 0% |
| chat | none | 40 | 50% | 0% | 50% | 0% |
| chat | relevant | 20 | 0% | 0% | 100% | 0% |
| chat | target_removed | 10 | 100% | 0% | 0% | 0% |
| files | irrelevant | 50 | 20% | 0% | 80% | 0% |
| files | none | 40 | 50% | 0% | 50% | 0% |
| files | relevant | 20 | 0% | 5% | 95% | 0% |
| files | target_removed | 10 | 100% | 0% | 0% | 0% |
| inbox | irrelevant | 40 | 0% | 0% | 100% | 0% |
| inbox | none | 40 | 50% | 0% | 50% | 0% |
| inbox | relevant | 20 | 0% | 5% | 95% | 0% |
| shop | irrelevant | 70 | 29% | 0% | 71% | 0% |
| shop | none | 60 | 50% | 0% | 50% | 0% |
| shop | relevant | 70 | 14% | 10% | 76% | 0% |
| shop | target_removed | 10 | 0% | 0% | 100% | 0% |
| tickets | irrelevant | 40 | 50% | 0% | 50% | 0% |
| tickets | none | 40 | 50% | 0% | 50% | 0% |
| tickets | relevant | 30 | 67% | 0% | 33% | 0% |
| tickets | target_removed | 10 | 0% | 0% | 100% | 0% |

## Pixel change at the handoff

Share of landed changes on which a pixel guard with each threshold would fire. Harmless: no change to the target (cosmetic or irrelevant). Relevant: the target moved or went away.

| domain | > 0.005 harmless / relevant | > 0.02 harmless / relevant | > 0.05 harmless / relevant | > 0.1 harmless / relevant |
|---|---|---|---|---|
| calendar | 97% / 96% | 45% / 3% | 33% / 0% | 0% / 0% |
| chat | 86% / 67% | 86% / 67% | 46% / 24% | 0% / 0% |
| files | 86% / 67% | 86% / 67% | 29% / 0% | 29% / 0% |
| inbox | 100% / 100% | 100% / 100% | 100% / 100% | 100% / 100% |
| shop | 80% / 88% | 80% / 88% | 80% / 88% | 30% / 0% |
| tickets | 67% / 50% | 67% / 2% | 33% / 0% | 32% / 0% |
| all | 85% / 78% | 78% / 55% | 55% / 41% | 31% / 8% |

