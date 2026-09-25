def validate(number: int, lower: int = 1, upper: int = 1):
    try:
        number = int(number)
    except ValueError:
        return False

    return max(lower, min(upper, number))
