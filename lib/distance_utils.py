def manhattan_distance(source: tuple[int, int], dest: tuple[int, int]) -> int:
    return abs(dest[0] - source[0]) + abs(dest[1] - source[1])
