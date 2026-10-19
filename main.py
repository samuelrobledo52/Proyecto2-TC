import argparse
import os
import sys
import time

import arbol
from cnf import a_cnf
from cyk import cyk, indices, texto_tabla, tokenizar
from gramatica import guardar, leer

salida_txt = []


def mostrar(texto=''):
    print(texto)
    salida_txt.append(texto)


def titulo(texto):
    mostrar()
    mostrar(texto)
    mostrar('-' * len(texto))


def leer_frases(ruta):
    with open(ruta, encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip() and not l.startswith('#')]


def procesar(g, unitarias, binarias, frase, n, carpeta):
    titulo(f'Frase {n}: {frase}')
    palabras = tokenizar(frase, g.terminales())
    mostrar('Tokens: ' + (' '.join(palabras) if palabras else '(vacía)'))
    desconocidas = [p for p in palabras if p not in unitarias]
    if desconocidas:
        mostrar('Símbolos que no están en la gramática: ' + ', '.join(desconocidas))
    inicio = time.perf_counter()
    acepta, tabla = cyk(g, palabras, unitarias, binarias)
    ms = (time.perf_counter() - inicio) * 1000
    if tabla:
        mostrar()
        mostrar(texto_tabla(tabla, palabras))
    mostrar()
    mostrar('Resultado: ' + ('SÍ' if acepta else 'NO'))
    mostrar(f'Tiempo CYK: {ms:.4f} ms')
    if acepta and tabla:
        raiz = arbol.construir(tabla, g.inicial, 0, len(palabras) - 1)
        mostrar()
        mostrar('Parse tree:')
        mostrar(arbol.texto(raiz))
        mostrar()
        mostrar(arbol.corchetes(raiz))
        imagen = arbol.dibujar(raiz, ' '.join(palabras), os.path.join(carpeta, f'arbol_{n}'))
        mostrar('Imagen: ' + (imagen if imagen else 'no se generó (falta Graphviz), quedó el .dot'))
    return acepta, ms


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    p = argparse.ArgumentParser(description='Convierte una CFG a CNF y valida frases con CYK')
    p.add_argument('gramatica', help='archivo con la gramática, una producción por línea')
    p.add_argument('frase', nargs='*', help='frase a validar (si no se da, se piden por consola)')
    p.add_argument('-f', '--frases', help='archivo con una frase por línea')
    p.add_argument('-o', '--salida', default='salida', help='carpeta para resultados e imágenes')
    args = p.parse_args()

    try:
        g = leer(args.gramatica)
    except (OSError, ValueError) as e:
        print(f'Error al leer la gramática: {e}')
        sys.exit(1)
    os.makedirs(args.salida, exist_ok=True)

    titulo('Gramática original')
    mostrar(str(g))
    mostrar()
    mostrar('Inicial: ' + g.inicial)
    mostrar('Variables: ' + ', '.join(g.variables()))
    mostrar('Terminales: ' + ', '.join(g.terminales()))
    mostrar('¿Ya está en CNF? ' + ('sí' if g.es_cnf() else 'no'))

    inicio = time.perf_counter()
    cnf, pasos = a_cnf(g)
    ms_cnf = (time.perf_counter() - inicio) * 1000
    for n, (nombre, paso, detalle) in enumerate(pasos, 1):
        titulo(f'Paso {n}: {nombre}')
        mostrar(detalle)
        mostrar()
        mostrar(str(paso))
    titulo('Gramática en CNF')
    mostrar(str(cnf))
    mostrar()
    mostrar(f'Producciones: {g.total()} -> {cnf.total()}   Tiempo de conversión: {ms_cnf:.4f} ms')
    guardar(cnf, os.path.join(args.salida, 'gramatica_cnf.txt'))

    unitarias, binarias = indices(cnf)
    frases = []
    if args.frase:
        frases.append(' '.join(args.frase))
    if args.frases:
        frases.extend(leer_frases(args.frases))

    resumen = []
    if frases:
        for n, frase in enumerate(frases, 1):
            resumen.append((frase, *procesar(cnf, unitarias, binarias, frase, n, args.salida)))
    else:
        n = 1
        while True:
            try:
                frase = input('\nIngrese una frase (Enter vacío para salir): ').strip()
            except EOFError:
                break
            if not frase:
                break
            resumen.append((frase, *procesar(cnf, unitarias, binarias, frase, n, args.salida)))
            n += 1

    if len(resumen) > 1:
        titulo('Resumen')
        ancho = max(len(f) for f, _, _ in resumen)
        for frase, acepta, ms in resumen:
            mostrar(f'{frase.ljust(ancho)}  {"SÍ" if acepta else "NO":<3} {ms:9.4f} ms')

    with open(os.path.join(args.salida, 'resultados.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(salida_txt) + '\n')


if __name__ == '__main__':
    main()
