"""
So here's my idea, we precompute the costs array since that's a one time thing.
Then iterate across the list of costs with two pointers.
Move a pointer across, shift the back pointer if the cost is too high.
"""
import cProfile
import random

def max_substring(s, t, max_cost):
  costs = [abs(ord(a) - ord(b)) for a, b in zip(s, t)]
  a, max_length, current_cost = 0, 0, 0
  for i, cost in enumerate(costs):
    current_cost += cost
    while current_cost > max_cost:
      current_cost -= costs[a]
      a += 1
    max_length = max(max_length, i + 1 - a)

  return max_length

"""
Weha tests
"""
s = "krpgjbjjznpzdfy" * 2000
t = "nxargkbydxmsgby" * 2000

z1 = "cbcabcdbcc"
z2 = "aaabcdfaaa"

#print(f"{s}, {t}, Expected: 4, Actual: {max_substring(s, t, 14)}")
cProfile.run('max_substring(s, t, 14)')
