"""
Distinct Islands problem that only pay to win cheaters can access.
"""

def build_island(sea, starting_point):
  island = set()
  grid_x, grid_y = len(sea[0]), len(sea)
  min_x, min_y = grid_x, grid_y
  max_x, max_y = 0, 0
  consider = [starting_point]
  while consider:
    x, y = consider.pop()

    if (x, y) in island:
      continue

    if x < 0 or x >= grid_x or y < 0 or y >= grid_y:
      continue

    if sea[y][x] == 0:
      continue

    if x < min_x:
      min_x = x
    if x > max_x:
      max_x = x
    if y < min_y:
      min_y = y
    if y > max_y:
      max_y = y

    island.add((x, y))
    consider.append((x - 1, y))
    consider.append((x + 1, y))
    consider.append((x, y - 1))
    consider.append((x, y + 1))

  return island, min_x, min_y, max_x - min_x, max_y - min_y

def clean_island(island, min_x, min_y, size_x, size_y):
  clean = set()
  for x, y in island:
    clean.add((x - min_x, y - min_y))
  return clean

def find_islands(sea):
  islands = []
  visited = set()
  for y, row in enumerate(sea):
    for x, col in enumerate(row):
      if sea[y][x] == 0 or (x, y) in visited:
        continue

      island, min_x, min_y, size_x, size_y = build_island(sea, (x, y))
      visited.update(island)
      clean = clean_island(island, min_x, min_y, size_x, size_y)
      if clean not in islands:
        islands.append(clean)

  return len(islands)

t2 = [[1, 1, 0, 1, 1], [1, 0, 0, 0, 0], [0 ,0, 0, 0, 1], [1, 1, 0, 1, 1]]
t3 = [[0, 1, 0], [1, 0, 1]]
print(f"Expected 3, got: {find_islands(t2)}")
print(f"Expected 1, got: {find_islands(t3)}")
