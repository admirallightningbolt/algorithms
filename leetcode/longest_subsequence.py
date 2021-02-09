"""
Backwards is no different than forwards but my brain is backwards so it makes
sense.
"""

def longest_subsequence(l, diff):
  state = {}
  max_length = 0
  for n in l[::-1]:
    target = n + diff
    state[n] = state.get(target, 0) + 1
    if state[n] > max_length:
      max_length = state[n]
  return max_length
