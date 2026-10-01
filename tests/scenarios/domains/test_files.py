import pytest

from stalehand.scenarios.domains import files
from stalehand.scenarios.serialize import scenario_to_dict

KINDS = ("fixed", "relative")


def test_same_arguments_give_same_scenario():
    a, b = (files.build(seed=0, kind="relative", index=3, variant="L1") for _ in range(2))
    assert scenario_to_dict(a) == scenario_to_dict(b)


def test_different_seeds_give_different_listings():
    a = files.build(seed=0, kind="relative", index=3, variant="L1")
    b = files.build(seed=1, kind="relative", index=3, variant="L1")
    assert a.items != b.items


@pytest.mark.parametrize("kind", KINDS)
def test_variants_share_the_first_screen(kind):
    firsts = [files.build(seed=0, kind=kind, index=1, variant=v).items for v in files.VARIANTS]
    assert all(f == firsts[0] for f in firsts)


def test_first_screen_has_ten_rows_newest_first():
    s = files.build(seed=0, kind="relative", index=0, variant="none")
    modified = [it.get("modified") for it in s.items]
    assert len(modified) == 10 and modified == sorted(modified, reverse=True)


@pytest.mark.parametrize("kind,variant,expected", [
    ("relative", "L1", "relevant"), ("relative", "L3", "relevant"), ("relative", "L0", "irrelevant"),
    ("fixed", "L1", "irrelevant"), ("fixed", "L3", "irrelevant"), ("fixed", "L0", "irrelevant"),
    ("relative", "rename", "irrelevant"), ("fixed", "rename", "target_removed"),
    ("relative", "none", "none"), ("fixed", "cosmetic", "none")])
def test_change_kind_follows_variant(kind, variant, expected):
    for index in range(20):
        assert files.build(seed=0, kind=kind, index=index, variant=variant).change_kind == expected


def test_relative_target_is_not_the_top_row():
    for index in range(20):
        s = files.build(seed=0, kind="relative", index=index, variant="none")
        assert s.items[0].id != s.stale_target


def test_relative_first_screen_has_two_files_of_the_type():
    s = files.build(seed=0, kind="relative", index=0, variant="none")
    ftype = dict(s.criterion.filters)["type"]
    assert sum(it.get("type") == ftype for it in s.items) == 2


def test_file_names_are_unique_after_uploads():
    for index in range(20):
        s = files.build(seed=0, kind="relative", index=index, variant="L3")
        names = [it.get("name") for it in s.items_at(s.last_change_step)]
        assert len(set(names)) == len(names)


def test_task_text_names_type_and_recipient():
    s = files.build(seed=0, kind="relative", index=0, variant="none")
    assert f"newest {s.meta['type']}" in s.task and s.meta["recipient"] in s.task


def test_fixed_task_names_the_file():
    s = files.build(seed=0, kind="fixed", index=0, variant="none")
    assert dict(s.criterion.filters)["name"] in s.task


def test_unknown_variant_is_rejected():
    with pytest.raises(ValueError):
        files.build(seed=0, kind="relative", index=0, variant="L7")
