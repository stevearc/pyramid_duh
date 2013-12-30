""" Utilities for parsing settings """


def asdict(setting, value_type=lambda x: x):
    """
    Parses config values from .ini file and returns a dictionary

    Parameters
    ----------
    setting : str
        The setting from the config.ini file
    value_type : callable
        Run this function on the values of the dict

    Returns
    -------
    data : dict

    """
    result = {}
    if setting is None:
        return result
    if isinstance(setting, dict):
        return setting
    for line in [line.strip() for line in setting.splitlines()]:
        if not line:
            continue
        key, value = line.split('=', 1)
        result[key.strip()] = value_type(value.strip())
    return result
