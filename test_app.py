def is_palindrome(input_string: str) -> bool:
    """
    Check if a given string is a palindrome.

    Args:
        input_string (str): String to check

    Returns:
        bool: True if input string is a palindrome, False otherwise
    """
    cleaned = input_string.replace(" ", "").lower()
    return cleaned == cleaned[::-1]

def dictionary_merge(dict1: dict, dict2: dict) -> dict:
    """
    Merge two dictionaries. In case of conflicts, values from the second dictionary will overwrite the ones from the first.

    Args:
        dict1 (dict): First dictionary
        dict2 (dict): Second dictionary

    Returns:
        dict: Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result