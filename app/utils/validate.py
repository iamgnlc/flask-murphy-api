def validate(number: int, min: int = 1, max: int = 1):
    try:
        number = int(number)
    except ValueError:
        return False

    if number > max:
        number = max

    if number < min:
        number = min

    return number
