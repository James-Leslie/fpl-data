from fpl_data.utils import drop_keys


def test_drop_keys():
    # Test case 1: Drop single key
    dictionary = {'a': 1, 'b': 2, 'c': 3}
    keys = ['b']
    expected_result = {'a': 1, 'c': 3}
    assert drop_keys(dictionary, keys) == expected_result

    # Test case 2: Drop multiple keys
    dictionary = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    keys = ['b', 'c']
    expected_result = {'a': 1, 'd': 4}
    assert drop_keys(dictionary, keys) == expected_result

    # Test case 3: Empty dictionary
    dictionary = {}
    keys = ['a', 'b', 'c']
    expected_result = {}
    assert drop_keys(dictionary, keys) == expected_result

    # Test case 4: Empty keys list
    dictionary = {'a': 1, 'b': 2, 'c': 3}
    keys = []
    expected_result = {'a': 1, 'b': 2, 'c': 3}
    assert drop_keys(dictionary, keys) == expected_result

    # Test case 5: Dictionary with non-string keys
    dictionary = {1: 'one', 2: 'two', 3: 'three'}
    keys = [2, 3]
    expected_result = {1: 'one'}
    assert drop_keys(dictionary, keys) == expected_result
