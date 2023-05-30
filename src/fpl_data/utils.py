def drop_keys(d, keys):
    '''Drop keys from a dictionary'''
    return {k: v for k, v in d.items() if k not in keys}
