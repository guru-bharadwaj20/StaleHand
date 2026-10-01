from stalehand.scenarios.domains.inbox_data import RECIPIENTS, SENDERS, SNIPPETS, TOPICS


def test_senders_are_unique():
    assert len(set(SENDERS)) == len(SENDERS) == 40


def test_topics_and_subjects_are_unique():
    assert len({t for t, _ in TOPICS}) == len({s for _, s in TOPICS}) == len(TOPICS) == 50


def test_pools_are_not_empty():
    assert SNIPPETS and RECIPIENTS
