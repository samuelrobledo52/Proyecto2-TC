import shutil
import subprocess


def construir(tabla, simbolo, i, j):
    entrada = tabla[i][j][simbolo]
    if len(entrada) == 1:
        return (simbolo, [(entrada[0], [])])
    k, b, c = entrada
    return (simbolo, [construir(tabla, b, i, k), construir(tabla, c, k + 1, j)])


def texto(nodo, prefijo='', ultimo=True, raiz=True):
    etiqueta, hijos = nodo
    if raiz:
        lineas = [etiqueta]
        nuevo = ''
    else:
        lineas = [prefijo + ('└── ' if ultimo else '├── ') + etiqueta]
        nuevo = prefijo + ('    ' if ultimo else '│   ')
    for n, h in enumerate(hijos):
        lineas.extend(texto(h, nuevo, n == len(hijos) - 1, False))
    return lineas if not raiz else '\n'.join(lineas)


def corchetes(nodo):
    etiqueta, hijos = nodo
    if not hijos:
        return etiqueta
    return '[' + etiqueta + ' ' + ' '.join(corchetes(h) for h in hijos) + ']'


def dot(nodo, titulo):
    lineas = ['digraph arbol {', '  graph [fontname="Helvetica"];', '  node [fontname="Helvetica"];', '  edge [arrowhead=none];',
              f'  labelloc="t"; label="{escapar(titulo)}";']
    contador = [0]

    def visitar(n):
        etiqueta, hijos = n
        mi_id = f'n{contador[0]}'
        contador[0] += 1
        if hijos:
            lineas.append(f'  {mi_id} [label="{escapar(etiqueta)}", shape=ellipse];')
        else:
            lineas.append(f'  {mi_id} [label="{escapar(etiqueta)}", shape=box, style=filled, fillcolor="#e8f0fe"];')
        for h in hijos:
            hijo_id = visitar(h)
            lineas.append(f'  {mi_id} -> {hijo_id};')
        return mi_id

    visitar(nodo)
    lineas.append('}')
    return '\n'.join(lineas)


def escapar(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def dibujar(nodo, titulo, ruta_sin_ext):
    fuente = dot(nodo, titulo)
    with open(ruta_sin_ext + '.dot', 'w', encoding='utf-8') as f:
        f.write(fuente)
    if not shutil.which('dot'):
        return None
    subprocess.run(['dot', '-Tpng', ruta_sin_ext + '.dot', '-o', ruta_sin_ext + '.png'], check=True)
    return ruta_sin_ext + '.png'
