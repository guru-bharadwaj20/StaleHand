#!/usr/bin/env bash
# Shop tasks on a relative criterion (cheapest, highest rated), rerun after the shop stopped mentioning sorting.
# The rows are byte-identical to the matching rows of shop.jsonl; only the file paths, and so the job ids, differ.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m stalehand scenarios --domain shop --n 5 --seed 0 --kinds cheapest,highest_rated --out shop_relative.jsonl
rm -rf shards_shop_rerun && mkdir shards_shop_rerun
split -l 10 -d -a 2 --additional-suffix .jsonl shop_relative.jsonl shards_shop_rerun/shop-relative-
