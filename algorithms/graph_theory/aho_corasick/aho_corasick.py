"""
An implementation of the aho corasick automaton
for string matching.

All of this, for 50 hacker rank points.
SMH
"""
import collections
import time


class Trie:

  def __init__(self):
    self.nodes = {}
    self.nodes[""] = TrieNode(value="", name="")
    self.root = self.nodes[""]
    return

  def get_longest_strict_suffix(self, node, letter):
    target_node = node.suffix_node
    target_name = f"{target_node.name}{letter}"

    if target_name in self.nodes:
      return self.nodes[target_name]

    while target_node.name != self.root.name:
      target_node = target_node.suffix_node
      target_name = f"{target_node.name}{letter}"
      if target_name in self.nodes:
        return self.nodes[target_name]

    return self.root

  def construct(self, keywords):
    sorted_keywords = sorted(keywords)
    word_length = []
    max_length = 0
    for word in sorted_keywords:
      l = len(word)
      word_length.append(l)
      if l > max_length:
        max_length = l

    start = 0
    end = len(sorted_keywords)
    for i in range(max_length):
      for j in range(start, end):
        word = sorted_keywords[j]
        word_len = word_length[j]
        if i >= word_len:
          start += 1
          continue

        node_name = word[:i+1]
        if node_name in self.nodes:
          continue

        node = TrieNode(
          value=word[i],
          name=node_name,
          output=(i == word_len - 1)
        )

        parent_name = word[:i]

        if parent_name == self.root.name:
          node.suffix_node = self.root
        else:
          node.suffix_node = self.get_longest_strict_suffix(self.nodes[parent_name], node.value)
          node.output_node = node.suffix_node if node.suffix_node.output else node.suffix_node.output_node

        self.nodes[node_name] = node
    return

  def render(self, fname):
    """Renders the trie to a graphviz diagram."""
    # Putting the import here so I can copy paste into hackerrank easily.
    from graphviz import Digraph
    d = Digraph()
    for name, node in self.nodes.items():
      if node.output:
        d.node(name, node.value, {"color": "lightblue2", "style": "filled"})
      else:
        d.node(name, node.value)

      # Render child edges
      for child in node.children:
        d.edge(name, child.name)

      # Render output & suffix links
      if node.suffix_node:
        d.edge(name, node.suffix_node.name, None, {"color": "blue", "constraint": "false"})
      if node.output_node:
        d.edge(name, node.output_node.name, None, {"color": "orange", "constraint": "false"})

    d.render(fname)
    return

  def get_occurrences(self, search):
    """Walks through the string and gets all occurences."""
    current_node = self.root
    occurrences = collections.defaultdict(int)
    for letter in search:
      target_name = f"{current_node.name}{letter}"
      # If the node exists we want to update occurences.
      # We need to follow all output links and update
      # the occurences for those as well.
      if target_name in self.nodes:
        current_node = self.nodes[target_name]
        self.count(occurrences, current_node)
        continue


      if current_node == self.root:
        continue

      current_node = self.get_longest_strict_suffix(current_node, letter)
      if current_node != self.root:
        self.count(occurrences, current_node)
    return occurrences

  def count(self, occurrences, current_node):
    if current_node.output:
      occurrences[current_node.name] += 1
    if current_node.output_node:
      tmp = current_node
      while tmp.output_node:
        occurrences[tmp.output_node.name] += 1
        tmp = tmp.output_node
    return




class TrieNode:

  __slots__ = ("name", "value", "output", "output_node", "suffix_node")

  def __init__(self, value=None, name=None,  output=False):
    self.name = name
    self.value = value
    # Determines if this is an output keyword.
    self.output = output
    # Edges for outputs & longest strict suffixes.
    self.output_node = None
    self.suffix_node = None
    return

  def __repr__(self):
    return self.name

  def __eq__(self, obj):
    return self.name == obj.name

  def __hash__(self):
    return hash(self.name)
