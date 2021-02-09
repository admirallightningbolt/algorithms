"""
A class for represnting and building nfas.
"""
import collections

from graphviz import Digraph
from pprint import pprint

class Node:
  """It's a node!

  In this case we only need to track a number just to identify the node.
  """

  def __init__(self, number):
    self.number = number

  def __hash__(self):
    return self.number

  def __repr__(self):
    return f"N({self.number})"

class Ticker:
  """An unnecessary helper class that maintains state to get sequential numbers."""

  def __init__(self):
    self.number = -1

  def next(self):
    self.number += 1
    return self.number


class Edge:
  """It's an edge!

  Special handling is done for epsilon values.
  """

  def __init__(self, source, sink, value):
    self.source = source
    self.sink = sink
    # Epsilon transitions are tracked by the literal string "epsilon".
    self.value = "ε" if value == "epsilon" else value
    return

  def is_epsilon(self):
    return self.value == "ε"

  def __repr__(self):
    return f"({self.source}, {self.sink}, {self.value})"

  def __hash__(self):
    return hash((self.source, self.sink))

class NFA:
  """A class representing a non-deterministic finite state automaton.

  Tracks edges from both incoming and outgoing directions.
  Can be mutated directly via helper methods:
    add_node()
    add_edge()
    remove_edge()
  or combined with other automaton:
    nfa_or()
    nfa_and()
    star()
  """

  def __init__(self, ticker):
    self.ticker = ticker
    self.start = Node(self.ticker.next())
    self.end = Node(self.ticker.next())
    self.nodes = set([self.start, self.end])
    self.outgoing_edges = collections.defaultdict(set)
    self.incoming_edges = collections.defaultdict(set)

  def render(self, fname):
    """Renders the automaton to a graph using graphviz."""
    d = Digraph()
    d.graph_attr["rankdir"] = "LR"
    for node in self.nodes:
      options = {}
      if node == self.start or node == self.end:
        options["style"] = "filled"
        options["color"] = "lightblue2" if node == self.start else "red"
      d.node(str(node.number), str(node.number), options)

    for source, edges in self.outgoing_edges.items():
      for edge in edges:
        d.edge(str(edge.source.number), str(edge.sink.number), label=edge.value)

    d.render(fname)


  def add_node(self):
    """Adds and returns a new node."""
    n = Node(self.ticker.next())
    self.nodes.add(n)
    return n


  def add_edge(self, source, sink, value):
    """Adds an edge, tracking by both incoming and outgoing."""
    e = Edge(source, sink, value)
    self.outgoing_edges[source].add(e)
    self.incoming_edges[sink].add(e)
    return e


  def remove_edge(self, edge):
    """Deletes an edge from both outgoing & incoming."""
    self.outgoing_edges[edge.source].remove(edge)
    self.incoming_edges[edge.sink].remove(edge)


  def from_a(self, a):
    """Creates a simple NFA from a single value."""
    self.add_edge(self.start, self.end, a)


  def merge(self, nfa):
    """Merges in all nodes and edges from another automaton."""
    self.nodes.update(nfa.nodes)
    for sink, edges in nfa.incoming_edges.items():
      self.incoming_edges[sink].update(edges)

    for source, edges in nfa.outgoing_edges.items():
      self.outgoing_edges[source].update(edges)


  def merge_node(self, n1, n2):
    """Merges two nodes.

    This shifts all the edges going into and out of n2.
    All outgoing edges (n2 -> somenode) are updated to (n1 -> somenode)
    All incoming edges (somenode -> n2) are updated to (somenode -> n1)
    """
    edges = self.outgoing_edges[n2].copy()
    for edge in edges:
      self.remove_edge(edge)
      self.add_edge(n1, edge.sink, edge.value)

    edges = self.incoming_edges[n2].copy()
    for edge in edges:
      self.remove_edge(edge)
      self.add_edge(edge.source, n1, edge.value)

    self.nodes.remove(n2)


  def nfa_or(self, nfa):
    """Updates the current NFA to be a logical or of itself and the passed in nfa."""
    self.merge(nfa)
    new_start = self.add_node()
    self.add_edge(new_start, self.start, "epsilon")
    self.add_edge(new_start, nfa.start, "epsilon")
    self.start = new_start
    new_end = self.add_node()
    self.add_edge(self.end, new_end, "epsilon")
    self.add_edge(nfa.end, new_end, "epsilon")
    self.end = new_end


  def nfa_and(self, nfa):
    """Updates the current NFA to be directly followed by the passed in nfa."""
    self.merge(nfa)
    self.merge_node(self.end, nfa.start)
    self.end = nfa.end


  def star(self):
    """Allow the current NFA to match anynumber of times."""
    self.add_edge(self.end, self.start, "epsilon")
    self.add_edge(self.start, self.end, "epsilon")

def find_or_pos(regex):
  unmatched = 0
  for i, c in enumerate(regex):
    if c == "(":
      unmatched += 1
    elif c == ")":
      unmatched -= 1
    elif c == "|" and unmatched == 0:
      return i
  return -1

def find_split(regex):
  """Finds the splitting point for an AB regex.

  Assuming we have a regex that looks like
  ({garbage})({garbage})

  We find the position of the opening parenthesis of the second stanza.
  """
  unmatched = 1
  for i, c in enumerate(regex):
    if i == 0:
      continue
    if c == "(":
      if unmatched == 0:
        return i
      unmatched += 1
    elif c == ")":
      unmatched -= 1
  return -1


def parse_regex(ticker, regex=""):
  """Takes a regex as an input string and turns it into an nfa.

  Our alphabet only contains (ab), and there are three operators allowed:
  (R{1}R{2}) - Regex 2 should direclty follow regex 1.
  (R{1}|R{2}) - Either match regex 1 or 2.
  (R{1}*) - Match regex 1 0 or more times.

  All operators are wrapped in parenthesis, no more than two values can be
  inside a single set of parenthesis including stars. Some valid example:

  ((a*)|(ab))
  ((ab)*)

  The actual logic will be recursive, and will strip off parens and call the
  appropriate nfa logic based on the operator of the resulting expression.
  """
  if len(regex) == 1:
    n = NFA(ticker)
    n.from_a(regex)
    return n

  # Pop some parens
  regex = regex[1:-1]
  # If the last char is a star, apply the star operator to the result of the
  # NFA construction ofo the first bit.
  if regex[-1] == "*":
    n = parse_regex(ticker, regex=regex[:-1])
    n.star()
    return n

  # If there is a pipe operator not contained within parethensis, run or.
  pos = find_or_pos(regex)
  if pos != -1:
    n = parse_regex(ticker, regex=regex[:pos])
    q = parse_regex(ticker, regex=regex[pos + 1:])
    n.nfa_or(q)
    return n

  # If we get here, it must be R1 -> R2. First we check for our base case
  # here which is len == 2 i.e. either ab or ba.
  if len(regex) == 2:
    n = NFA(ticker)
    n.from_a(regex[0])
    q = NFA(ticker)
    q.from_a(regex[1])
    n.nfa_and(q)
    return n

  # Otherwise we need to find where to split by. We use similar logic
  split = find_split(regex)
  n = parse_regex(ticker, regex=regex[:split])
  q = parse_regex(ticker, regex=regex[split:])
  n.nfa_and(q)
  return n


if __name__ == "__main__":
  ticker = Ticker()
  nfa = parse_regex(ticker, "(((c*)(a*))b)")
  # nfa = parse_regex(ticker, "((ab)|((b|a)(b*)))")
  nfa.render("regex.gv")
