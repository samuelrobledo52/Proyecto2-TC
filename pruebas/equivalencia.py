import itertools
import os
import random
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from gramatica import Gramatica, agregar, leer
from cnf import a_cnf
from cyk import cyk, indices

def earley(g, w):
    P = g.producciones
    n = len(w)
    S = [set() for _ in range(n+1)]
    S[0].add(('#', (g.inicial,), 0, 0))
    for i in range(n+1):
        agenda = list(S[i])
        while agenda:
            it = agenda.pop()
            A, body, dot, org = it
            if dot < len(body):
                X = body[dot]
                if X in P:
                    for b in P[X]:
                        new = (X, b, 0, i)
                        if new not in S[i]: S[i].add(new); agenda.append(new)
                    for (B, bb, d2, o2) in list(S[i]):
                        if B == X and d2 == len(bb) and o2 == i:
                            new = (A, body, dot+1, org)
                            if new not in S[i]: S[i].add(new); agenda.append(new)
                elif i < n and w[i] == X:
                    S[i+1].add((A, body, dot+1, org))
            else:
                for (B, bb, d2, o2) in list(S[org]):
                    if d2 < len(bb) and bb[d2] == A:
                        new = (B, bb, d2+1, o2)
                        if new not in S[i]: S[i].add(new); agenda.append(new)
    return ('#', (g.inicial,), 1, 0) in S[n]

def rand_grammar(r):
    V = ['S','A','B','C','D'][:r.randint(2,5)]
    T = ['a','b','c'][:r.randint(1,3)]
    P = {}
    for v in V:
        for _ in range(r.randint(1,3)):
            L = r.choice([0,1,1,2,2,3,3,4])
            agregar(P, v, tuple(r.choice(V+T) for _ in range(L)))
    return Gramatica('S', P), T

r = random.Random(7)
total = fallos = 0
for t in range(3000):
    g, T = rand_grammar(r)
    cnf, _ = a_cnf(g)
    assert cnf.es_cnf(), str(cnf)
    u, b = indices(cnf)
    for L in range(0, 6):
        for w in itertools.product(T, repeat=L):
            total += 1
            e = earley(g, list(w))
            c = cyk(cnf, list(w), u, b)[0]
            if e != c:
                fallos += 1
                if fallos < 4: print('FALLO', w, e, c); print(g); print('--'); print(cnf)
print('cadenas probadas', total, 'fallos', fallos)
for nombre in ['1.txt', 'ingles.txt']:
    g = leer(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gramaticas', nombre))
    cnf, _ = a_cnf(g); u, b = indices(cnf); T = g.terminales()
    bad = 0; tot = 0
    for L in range(0, 7 if nombre=='1.txt' else 5):
        for w in itertools.product(T, repeat=L):
            tot += 1
            bad += earley(g, list(w)) != cyk(cnf, list(w), u, b)[0]
    print(nombre, tot, 'fallos', bad)
