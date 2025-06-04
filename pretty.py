# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Utilities for string manipulation in the DSL."""

MAP_SYMBOL = {
    'T': 'perp',
    'P': 'para',
    'D': 'cong',
    'S': 'simtri',
    'I': 'circle',
    'M': 'midp',
    'O': 'cyclic',
    'C': 'coll',
    '^': 'eqangle',
    '/': 'eqratio',
    '%': 'eqratio',
    '=': 'contri',
    'X': 'collx',
    'A': 'acompute',
    'R': 'rcompute',
    'Q': 'fixc',
    'E': 'fixl',
    'V': 'fixb',
    'H': 'fixt',
    'Z': 'fixp',
    'Y': 'ind',
}


def map_symbol(c: str) -> str:
  return MAP_SYMBOL[c]


def map_symbol_inv(c: str) -> str:
  return {v: k for k, v in MAP_SYMBOL.items()}[c]


def _gcd(x: int, y: int) -> int:
  while y:
    x, y = y, x % y
  return x


def simplify(n: int, d: int) -> tuple[int, int]:
  g = _gcd(n, d)
  return (n // g, d // g)


def pretty2r(a: str, b: str, c: str, d: str) -> str:
  if b in (c, d):
    a, b = b, a

  if a == d:
    c, d = d, c

  return f'{a} {b} {c} {d}'


def pretty2a(a: str, b: str, c: str, d: str) -> str:
  if b in (c, d):
    a, b = b, a

  if a == d:
    c, d = d, c

  return f'{a} {b} {c} {d}'


def pretty_angle(a: str, b: str, c: str, d: str) -> str:
  if b in (c, d):
    a, b = b, a
  if a == d:
    c, d = d, c

  if a == c:
    return f'\u2220{b}{a}{d}'
  return f'\u2220({a}{b}-{c}{d})'


def pretty_nl(name: str, args: list[str]) -> str:
  """Natural lang formatting a predicate."""
  if name == 'aconst':
    a, b, c, d, y = args
    return f'{pretty_angle(a, b, c, d)} = {y}'
  if name == 'rconst':
    a, b, c, d, y = args
    return f'{a}{b}:{c}{d} = {y}'
  if name == 'acompute':
    a, b, c, d = args
    return f'{pretty_angle(a, b, c, d)}'
  if name in ['coll', 'C']:
    return '' + ','.join(args) + ' are collinear'
  if name == 'collx':
    return '' + ','.join(list(set(args))) + ' are collinear'
  if name in ['cyclic', 'O']:
    return '' + ','.join(args) + ' are concyclic'
  if name in ['midp', 'midpoint', 'M']:
    x, a, b = args
    return f'{x} is midpoint of {a}{b}'
  if name in ['eqangle', 'eqangle6', '^']:
    a, b, c, d, e, f, g, h = args
    return f'{pretty_angle(a, b, c, d)} = {pretty_angle(e, f, g, h)}'
  if name in ['eqratio', 'eqratio6', '/']:
    return '{}{}:{}{} = {}{}:{}{}'.format(*args)
  if name == 'eqratio3':
    a, b, c, d, o, o = args  # pylint: disable=redeclared-assigned-name
    return f'S {o} {a} {b} {o} {c} {d}'
  if name in ['cong', 'D']:
    a, b, c, d = args
    return f'{a}{b} = {c}{d}'
  if name in ['perp', 'T']:
    if len(args) == 2:  # this is algebraic derivation.
      ab, cd = args  # ab = 'd( ... )'
      return f'{ab} \u27c2 {cd}'
    a, b, c, d = args
    return f'{a}{b} \u27c2 {c}{d}'
  if name in ['para', 'P']:
    if len(args) == 2:  # this is algebraic derivation.
      ab, cd = args  # ab = 'd( ... )'
      return f'{ab} \u2225 {cd}'
    a, b, c, d = args
    return f'{a}{b} \u2225 {c}{d}'
  if name in ['simtri2', 'simtri', 'simtri*']:
    a, b, c, x, y, z = args
    return f'\u0394{a}{b}{c} is similar to \u0394{x}{y}{z}'
  if name in ['contri2', 'contri', 'contri*']:
    a, b, c, x, y, z = args
    return f'\u0394{a}{b}{c} is congruent to \u0394{x}{y}{z}'
  if name in ['circle', 'I']:
    o, a, b, c = args
    return f'{o} is the circumcenter of \\Delta {a}{b}{c}'
  if name == 'foot':
    a, b, c, d = args
    return f'{a} is the foot of {b} on {c}{d}'


def pretty(txt: str) -> str:
  """Pretty formating a predicate string."""
  if isinstance(txt, str):
    txt = txt.split(' ')
  name, *args = txt
  if name == 'ind':
    return 'Y ' + ' '.join(args)
  if name in ['fixc', 'fixl', 'fixb', 'fixt', 'fixp']:
    return map_symbol_inv(name) + ' ' + ' '.join(args)
  if name == 'acompute':
    a, b, c, d = args
    return 'A ' + ' '.join(args)
  if name == 'rcompute':
    a, b, c, d = args
    return 'R ' + ' '.join(args)
  if name == 'aconst':
    a, b, c, d, y = args
    return f'^ {pretty2a(a, b, c, d)} {y}'
  if name == 'rconst':
    a, b, c, d, y = args
    return f'/ {pretty2r(a, b, c, d)} {y}'
  if name == 'coll':
    return 'C ' + ' '.join(args)
  if name == 'collx':
    return 'X ' + ' '.join(args)
  if name == 'cyclic':
    return 'O ' + ' '.join(args)
  if name in ['midp', 'midpoint']:
    x, a, b = args
    return f'M {x} {a} {b}'
  if name == 'eqangle':
    a, b, c, d, e, f, g, h = args
    return f'^ {pretty2a(a, b, c, d)} {pretty2a(e, f, g, h)}'
  if name == 'eqratio':
    a, b, c, d, e, f, g, h = args
    return f'/ {pretty2r(a, b, c, d)} {pretty2r(e, f, g, h)}'
  if name == 'eqratio3':
    a, b, c, d, o, o = args  # pylint: disable=redeclared-assigned-name
    return f'S {o} {a} {b} {o} {c} {d}'
  if name == 'cong':
    a, b, c, d = args
    return f'D {a} {b} {c} {d}'
  if name == 'perp':
    if len(args) == 2:  # this is algebraic derivation.
      ab, cd = args  # ab = 'd( ... )'
      return f'T {ab} {cd}'
    a, b, c, d = args
    return f'T {a} {b} {c} {d}'
  if name == 'para':
    if len(args) == 2:  # this is algebraic derivation.
      ab, cd = args  # ab = 'd( ... )'
      return f'P {ab} {cd}'
    a, b, c, d = args
    return f'P {a} {b} {c} {d}'
  if name in ['simtri2', 'simtri', 'simtri*']:
    a, b, c, x, y, z = args
    return f'S {a} {b} {c} {x} {y} {z}'
  if name in ['contri2', 'contri', 'contri*']:
    a, b, c, x, y, z = args
    return f'= {a} {b} {c} {x} {y} {z}'
  if name == 'circle':
    o, a, b, c = args
    return f'I {o} {a} {b} {c}'
  if name == 'foot':
    a, b, c, d = args
    return f'F {a} {b} {c} {d}'
  return ' '.join(txt)


def cn_pretty(txt: str, eng=False) -> str:
  """Pretty formating a predicate string."""
  if isinstance(txt, str):
    txt = txt.split(' ')
  name, *args = txt
  if name == 'ind':
    return 'Y ' + ' '.join(args)
  if name in ['fixc', 'fixl', 'fixb', 'fixt', 'fixp']:
    return map_symbol_inv(name) + ' ' + ' '.join(args)
  if name == 'acompute':
    a, b, c, d = args
    # return 'A ' + ' '.join(args)
    al = [a, b, c, d]
    v1 = [i for i in al if al.count(i) > 1]
    if v1:
      e1 = [i for i in al if i != v1[0]]
      return f"\u2220{e1[0]}{v1[0]}{e1[1]}"
    else:
      return f''.join(args)
  if name == 'rcompute':
    a, b, c, d = args
    # return 'R ' + ' '.join(args)
    return f'{a}{b}:{c}{d}'
  if name == 'aconst':
    a, b, c, d, y = args
    al = f'{pretty2a(a, b, c, d)}'.split(" ")
    v1 = [i for i in al if al.count(i) > 1]
    if v1:
      e1 = [i for i in al if i != v1[0]]
      return f"\u2220{e1[0]}{v1[0]}{e1[1]} = {y}"
    else:
      if eng:
        return f"the intersection angle of {al[0]}{al[1]} and {al[2]}{al[3]} is equal to {y}"
      else:
        return f"{al[0]}{al[1]}到{al[2]}{al[3]}所成的夹角 = {y}"
      # return f'^ {pretty2a(a, b, c, d)} {y}'
  if name == 'rconst':
    a, b, c, d, y = args
    r1 = f'{pretty2r(a, b, c, d)}'.split(" ")
    # return f'/ {pretty2r(a, b, c, d)} {y}'
    return "".join(r1[:2])+"/"+"".join(r1[2:])+" = "+ y
  if name == 'coll':
    # return 'C ' + ' '.join(args)
    if eng:
      return ','.join(args)+" are on the same line"
    else:
      return ','.join(args)+"共线"
  if name == 'collx':
    # return 'X ' + ' '.join(args)
    if eng:
      return ','.join(args)+" are on the same line"
    else:
      return ','.join(args)+"共线"
  if name == 'cyclic':
    # return 'O ' + ' '.join(args)
    if eng:
      return ",".join(args)+" are on the same circle"
    else:
      return ",".join(args)+"共圆"
  if name in ['midp', 'midpoint']:
    x, a, b = args
    # return f'M {x} {a} {b}'
    if eng:
      return f'{x} is the midpoint of {a} and {b}'
    else:
      return f'{x}是{a}{b}的中点'
  if name == 'eqangle' or name[:7] == 'eqangle':
    a, b, c, d, e, f, g, h = args
    a1 = f'{pretty2a(a, b, c, d)}'.split(" ")
    a2 = f'{pretty2a(e, f, g, h)}'.split(" ")
    v1 = [i for i in a1 if a1.count(i) > 1]
    v2 = [i for i in a2 if a2.count(i) > 1]
    if v1 and v2:
      e1 = [i for i in a1 if i != v1[0]]
      e2 = [i for i in a2 if i != v2[0]]
      return f"\u2220{e1[0]}{v1[0]}{e1[1]}=\u2220{e2[0]}{v2[0]}{e2[1]}"
    elif v1:
      e1 = [i for i in a1 if i != v1[0]]
      if eng:
        return f'\u2220{e1[0]}{v1[0]}{e1[1]} equals the intersection angle of {a2[0]}{a2[1]} and {a2[2]}{a2[3]}'
      else:
        return f'\u2220{e1[0]}{v1[0]}{e1[1]}={a2[0]}{a2[1]}到{a2[2]}{a2[3]}所成的夹角'
    elif v2:
      e2 = [i for i in a2 if i != v2[0]]
      if eng:
        return f'the intersection angle of {a1[0]}{a1[1]} and {a1[2]}{a1[3]} is equal to \u2220{e2[0]}{v2[0]}{e2[1]}'
      else:
        return f'{a1[0]}{a1[1]}到{a1[2]}{a1[3]}所成的夹角=\u2220{e2[0]}{v2[0]}{e2[1]}'
    else:
      if eng:
        return f'the intersection angle of {a1[0]}{a1[1]} and {a1[2]}{a1[3]} is equal to the intersection angle of {a2[0]}{a2[1]} and {a2[2]}{a2[3]}'
      else:
        return f'{a1[0]}{a1[1]}到{a1[2]}{a1[3]}所成的夹角等于{a2[0]}{a2[1]}到{a2[2]}{a2[3]}所成的夹角'
  if name in ['eqratio','eqratio6'] :
    a, b, c, d, e, f, g, h = args
    r1 = f'{pretty2r(a, b, c, d)}'
    r2 = f'{pretty2r(e, f, g, h)}'
    # return f'/ {pretty2r(a, b, c, d)} {pretty2r(e, f, g, h)}'
    return "".join(r1.split(" ")[:2]) +"/"+"".join(r1.split(" ")[2:]) + " = " + "".join(r2.split(" ")[:2]) +"/"+"".join(r2.split(" ")[2:])
  if name == 'eqratio3':
    a, b, c, d, o, o = args  # pylint: disable=redeclared-assigned-name
    if eng:
      return f'\u0394{o}{a}{b} is similar to \u0394{o}{c}{d}'
    else:
      return f'\u0394{o}{a}{b}相似于\u0394{o}{c}{d}'
    # return f'S {o} {a} {b} {o} {c} {d}'
  if name == 'cong':
    a, b, c, d = args
    return f"{a}{b}={c}{d}"
    # return f'D {a} {b} {c} {d}'
  if name == 'perp':
    if len(args) == 2:  # this is algebraic derivation.
      ab, cd = args  # ab = 'd( ... )'
      return f'{ab}\u27c2{cd}'
      # return f'T {ab} {cd}'
    a, b, c, d = args
    # return f'T {a} {b} {c} {d}'
    return f'{a}{b}\u27c2{c}{d}'
  if name == 'para':
    if len(args) == 2:  # this is algebraic derivation.
      ab, cd = args  # ab = 'd( ... )'
      # return f'P {ab} {cd}'
      return f'{ab}\u2225{cd}'
    a, b, c, d = args
    # return f'P {a} {b} {c} {d}'
    return f'{a}{b}\u2225{c}{d}'
  if name in ['simtri2', 'simtri', 'simtri*']:
    a, b, c, x, y, z = args
    if eng:
      return f'\u0394{a}{b}{c} is similar to \u0394{x}{y}{z}'
    else:
      return f'\u0394{a}{b}{c}相似于\u0394{x}{y}{z}'
  if name in ['contri2', 'contri', 'contri*']:
    a, b, c, x, y, z = args
    # return f'{a}{b}{c}全等于{x}{y}{z}'
    if eng:
      return f'\u0394{a}{b}{c} and \u0394{x}{y}{z} are congruent triangles'
    else:
      return f'\u0394{a}{b}{c}全等于\u0394{x}{y}{z}'
  if name == 'circle':
    o, a, b, c = args
    if eng:
      return f'{o} is the circumcenter of \u0394{a}{b}{c}'
    else:
      return f'{o}是\u0394{a}{b}{c}的外接圆心'
  if name == 'foot':
    a, b, c, d = args
    if eng:
      return f'{a}{b}\u27c2{c}{d} with foot {a}'
    else:
      return f'{a}{b}\u27c2{c}{d}垂足是{a}'
  return ' '.join(txt)
