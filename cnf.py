from itertools import product

from gramatica import Gramatica, agregar

NOMBRES = {'(': 'L', ')': 'R', '+': 'P', '*': 'M', '-': 'N', '/': 'D', ',': 'K', ';': 'Q'}


def nombre_libre(base, usados):
    if base not in usados:
        return base
    i = 1
    while f'{base}{i}' in usados:
        i += 1
    return f'{base}{i}'


def anulables(g):
    nulos = set()
    cambio = True
    while cambio:
        cambio = False
        for a, cuerpos in g.producciones.items():
            if a not in nulos and any(all(s in nulos for s in c) for c in cuerpos):
                nulos.add(a)
                cambio = True
    return nulos


def nuevo_inicial(g):
    aparece = any(g.inicial in c for cuerpos in g.producciones.values() for c in cuerpos)
    if not aparece or g.inicial not in anulables(g):
        return g, None
    s0 = nombre_libre(g.inicial + '0', set(g.producciones))
    producciones = {s0: [(g.inicial,)]}
    producciones.update({a: list(c) for a, c in g.producciones.items()})
    return Gramatica(s0, producciones), s0


def eliminar_epsilon(g):
    nulos = anulables(g)
    producciones = {}
    for a, cuerpos in g.producciones.items():
        producciones[a] = []
        for c in cuerpos:
            opciones = [(s, None) if s in nulos else (s,) for s in c]
            for combo in product(*opciones):
                nuevo = tuple(s for s in combo if s is not None)
                if nuevo:
                    agregar(producciones, a, nuevo)
    if g.inicial in nulos:
        agregar(producciones, g.inicial, ())
    return Gramatica(g.inicial, producciones), nulos


def pares_unitarios(g):
    pares = [(a, a) for a in g.producciones]
    i = 0
    while i < len(pares):
        a, b = pares[i]
        for c in g.producciones.get(b, []):
            if len(c) == 1 and g.es_variable(c[0]) and (a, c[0]) not in pares:
                pares.append((a, c[0]))
        i += 1
    return pares


def eliminar_unitarias(g):
    pares = pares_unitarios(g)
    producciones = {a: [] for a in g.producciones}
    for a, b in pares:
        for c in g.producciones[b]:
            if not (len(c) == 1 and g.es_variable(c[0])):
                agregar(producciones, a, c)
    return Gramatica(g.inicial, producciones), pares


def eliminar_inutiles(g):
    generan = set()
    cambio = True
    while cambio:
        cambio = False
        for a, cuerpos in g.producciones.items():
            if a in generan:
                continue
            if any(all(not g.es_variable(s) or s in generan for s in c) for c in cuerpos):
                generan.add(a)
                cambio = True
    if g.inicial not in generan:
        return Gramatica(g.inicial, {g.inicial: []}), set(g.producciones) - {g.inicial}
    filtradas = {}
    for a, cuerpos in g.producciones.items():
        if a in generan:
            filtradas[a] = [c for c in cuerpos if all(not g.es_variable(s) or s in generan for s in c)]
    alcanzables = {g.inicial}
    pila = [g.inicial]
    while pila:
        a = pila.pop()
        for c in filtradas[a]:
            for s in c:
                if s in filtradas and s not in alcanzables:
                    alcanzables.add(s)
                    pila.append(s)
    producciones = {a: c for a, c in filtradas.items() if a in alcanzables}
    quitadas = set(g.producciones) - set(producciones)
    return Gramatica(g.inicial, producciones), quitadas


def terminales_a_variables(g):
    usados = set(g.producciones) | set(g.terminales())
    nuevas = {}
    producciones = {}
    for a, cuerpos in g.producciones.items():
        producciones[a] = []
        for c in cuerpos:
            if len(c) < 2:
                agregar(producciones, a, c)
                continue
            nuevo = []
            for s in c:
                if g.es_variable(s):
                    nuevo.append(s)
                    continue
                if s not in nuevas:
                    base = NOMBRES.get(s, 'T_' + s if s.isalnum() else 'T')
                    nuevas[s] = nombre_libre(base, usados)
                    usados.add(nuevas[s])
                nuevo.append(nuevas[s])
            agregar(producciones, a, tuple(nuevo))
    for s, v in nuevas.items():
        producciones[v] = [(s,)]
    return Gramatica(g.inicial, producciones), nuevas


def binarizar(g):
    usados = set(g.producciones) | set(g.terminales())
    cadenas = {}
    producciones = {a: [] for a in g.producciones}
    contador = [0]

    def variable_para(resto):
        if resto not in cadenas:
            contador[0] += 1
            v = nombre_libre(f'C{contador[0]}', usados)
            usados.add(v)
            cadenas[resto] = v
            cuerpo = resto if len(resto) == 2 else (resto[0], variable_para(resto[1:]))
            producciones[v] = [cuerpo]
        return cadenas[resto]

    for a, cuerpos in g.producciones.items():
        for c in cuerpos:
            if len(c) <= 2:
                agregar(producciones, a, c)
            else:
                agregar(producciones, a, (c[0], variable_para(c[1:])))
    return Gramatica(g.inicial, producciones), cadenas


def a_cnf(g):
    pasos = []
    g, s0 = nuevo_inicial(g)
    if s0:
        pasos.append(('Nuevo símbolo inicial', g, f'{s0} -> {g.producciones[s0][0][0]}'))
    g, nulos = eliminar_epsilon(g)
    pasos.append(('Eliminar producciones ε', g, 'anulables: ' + (', '.join(sorted(nulos)) or 'ninguna')))
    g, pares = eliminar_unitarias(g)
    pares_txt = ', '.join(f'({a},{b})' for a, b in pares if a != b)
    pasos.append(('Eliminar producciones unitarias', g, 'pares unitarios: ' + (pares_txt or 'ninguno')))
    g, quitadas = eliminar_inutiles(g)
    pasos.append(('Eliminar símbolos inútiles', g, 'eliminados: ' + (', '.join(sorted(quitadas)) or 'ninguno')))
    g, nuevas = terminales_a_variables(g)
    nuevas_txt = ', '.join(f'{v} -> {s}' for s, v in nuevas.items())
    pasos.append(('Terminales en cuerpos largos', g, 'nuevas: ' + (nuevas_txt or 'ninguna')))
    g, cadenas = binarizar(g)
    cadenas_txt = ', '.join(f'{v} -> {" ".join(r)}' for r, v in cadenas.items())
    pasos.append(('Cuerpos de largo 2', g, 'nuevas: ' + (cadenas_txt or 'ninguna')))
    return g, pasos
