def normalize(s):
    """Make all newlines equal to \\n"""

    return s.replace("\r\n", "\n").rstrip()
