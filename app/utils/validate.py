from flask import abort

def validate(number, min = 1, max = 1):
    try:
        number = int(number)
    except ValueError:
        abort(404)

    if number > max:
        number = max

    if number < min:
        number = min

    return number
