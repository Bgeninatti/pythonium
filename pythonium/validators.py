def number_between_zero_100(instance, attribute, value):
    return value >= 0 and value <= 100


def is_valid_position(instance, attribute, value):
    if value is None:
        return True
    return all(isinstance(v, int) for v in value) and len(value) == 3


def is_valid_ratio(instance, attribute, value):
    return value >= 0.0 and value <= 1.0
