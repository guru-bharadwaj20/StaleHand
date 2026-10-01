from stalehand.scenarios.domains.files_data import TYPES


def test_each_type_has_twelve_unique_names():
    for _, names in TYPES.values():
        assert len(set(names)) == len(names) == 12
