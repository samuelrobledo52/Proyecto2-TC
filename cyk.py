def indices(g):
    unitarias = {}
    binarias = {}
    for a, cuerpos in g.producciones.items():
        for c in cuerpos:
            if len(c) == 1:
                unitarias.setdefault(c[0], []).append(a)
            elif len(c) == 2:
                binarias.setdefault(c, []).append(a)
    return unitarias, binarias


def cyk(g, palabras, unitarias=None, binarias=None):
    if unitarias is None:
        unitarias, binarias = indices(g)
    n = len(palabras)
    if n == 0:
        return () in g.producciones.get(g.inicial, []), []
    tabla = [[{} for _ in range(n)] for _ in range(n)]
    for i, w in enumerate(palabras):
        for a in unitarias.get(w, []):
            tabla[i][i][a] = (w,)
    for largo in range(2, n + 1):
        for i in range(n - largo + 1):
            j = i + largo - 1
            celda = tabla[i][j]
            for k in range(i, j):
                izq = tabla[i][k]
                der = tabla[k + 1][j]
                if not izq or not der:
                    continue
                for b in izq:
                    for c in der:
                        for a in binarias.get((b, c), []):
                            if a not in celda:
                                celda[a] = (k, b, c)
    return g.inicial in tabla[0][n - 1], tabla


def tokenizar(frase, terminales):
    terminales = set(terminales)
    largos = sorted({len(t) for t in terminales}, reverse=True)
    tokens = []
    for trozo in frase.split():
        if trozo in terminales:
            tokens.append(trozo)
            continue
        if trozo.lower() in terminales:
            tokens.append(trozo.lower())
            continue
        partes = partir(trozo, terminales, largos) or partir(trozo.lower(), terminales, largos)
        if partes:
            tokens.extend(partes)
        elif trozo[-1] in '.!?' and len(trozo) > 1:
            tokens.extend(tokenizar(trozo[:-1], terminales))
        else:
            tokens.append(trozo)
    return tokens


def partir(texto, terminales, largos):
    partes = []
    i = 0
    while i < len(texto):
        for l in largos:
            if texto[i:i + l] in terminales:
                partes.append(texto[i:i + l])
                i += l
                break
        else:
            return None
    return partes


def texto_tabla(tabla, palabras):
    n = len(palabras)
    celdas = [[('{' + ', '.join(tabla[i][i + l].keys()) + '}' if tabla[i][i + l] else '∅')
               for i in range(n - l)] for l in range(n)]
    ancho = max(max(len(c) for fila in celdas for c in fila), max(len(p) for p in palabras)) + 2
    lineas = [' ' * 10 + ''.join(p.ljust(ancho) for p in palabras)]
    for l, fila in enumerate(celdas):
        lineas.append(f'largo {l + 1:<4}' + ''.join(c.ljust(ancho) for c in fila))
    return '\n'.join(lineas)
