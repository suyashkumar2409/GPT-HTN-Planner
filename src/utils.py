def comma_seperated_items(items):
    str = ''
    for item_idx in range(len(items)):
        str += items[item_idx]
        if item_idx != len(items) - 1:
            str += ', '
    return str
