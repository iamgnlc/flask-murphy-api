def validate(number, min = 1, max = 1):
    try:
        number = int(number)
    except ValueError:
        return False

    if number > max:
        number = max

    if number < min:
        number = min

    return number
