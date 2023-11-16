def sanitize(input_string, max_length):
    if len(input_string) > max_length:
        return input_string[:max_length - 3] + "..."
    else:
        return input_string