from stalehand.scenarios.domains.shop_data import CATEGORIES


def test_each_category_has_fifteen_unique_products():
    for names in CATEGORIES.values():
        assert len(set(names)) == len(names) == 15
