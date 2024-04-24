def create_message(data: dict[str, str]) -> str:
    """Create message using the given data dictionary and return the constructed message as a string.

    Parameters:
        data (dict[str, str]): The dictionary containing key-value pairs to construct the message.

    Returns:
        str: The constructed message as a string.
    """
    message = ""
    for key, value in data.items():
        message += f"{key}: {value}\n"
    return message
