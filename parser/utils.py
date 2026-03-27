def clear_spaces(string: str):
    if "  " in string: return clear_spaces(string.replace("  ", " "))
    else: return string.replace(" ,", ",")

def replace_collisions(string: str, collisions: dict[str, str]):
    for collision, new in collisions.items():
        if collision in string:
            string = replace_collisions(string.replace(collision, new), collisions)
    return string