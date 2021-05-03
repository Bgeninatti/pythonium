def number_between_zero_100(instance, attribute, value):
    return 0 <= value <= 100


def is_valid_ratio(instance, attribute, value):
    return 0.0 <= value <= 1.0
