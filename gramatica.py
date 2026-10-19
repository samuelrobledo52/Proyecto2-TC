EPS = 'ε'
VACIOS = {'e', 'ε', 'eps', 'epsilon', "''"}


class Gramatica:
    def __init__(self, inicial, producciones):
        self.inicial = inicial
        self.producciones = producciones

    def variables(self):
        return list(self.producciones)

    def terminales(self):
        vistos = []
        for cuerpos in self.producciones.values():
            for cuerpo in cuerpos:
                for s in cuerpo:
                    if s not in self.producciones and s not in vistos:
                        vistos.append(s)
        return vistos

    def es_variable(self, s):
        return s in self.producciones

    def copia(self):
        return Gramatica(self.inicial, {a: list(c) for a, c in self.producciones.items()})

    def total(self):
        return sum(len(c) for c in self.producciones.values())

    def es_cnf(self):
        for a, cuerpos in self.producciones.items():
            for c in cuerpos:
                if len(c) == 0 and a == self.inicial:
                    continue
                if len(c) == 1 and not self.es_variable(c[0]):
                    continue
                if len(c) == 2 and all(self.es_variable(s) for s in c):
                    continue
                return False
        return True

    def __str__(self):
        ancho = max(len(a) for a in self.producciones)
        lineas = []
        for a, cuerpos in self.producciones.items():
            texto = ' | '.join(' '.join(c) if c else EPS for c in cuerpos)
            lineas.append(f'{a.ljust(ancho)} -> {texto}')
        return '\n'.join(lineas)


def agregar(producciones, cabeza, cuerpo):
    lista = producciones.setdefault(cabeza, [])
    if cuerpo not in lista:
        lista.append(cuerpo)


def leer(ruta):
    producciones = {}
    inicial = None
    with open(ruta, encoding='utf-8') as f:
        for n, linea in enumerate(f, 1):
            linea = linea.strip()
            if not linea or linea.startswith('#'):
                continue
            linea = linea.replace('→', '->')
            if '->' not in linea:
                raise ValueError(f'línea {n}: falta "->"')
            cabeza, resto = linea.split('->', 1)
            cabeza = cabeza.strip()
            if not cabeza or ' ' in cabeza:
                raise ValueError(f'línea {n}: cabeza inválida "{cabeza}"')
            if inicial is None:
                inicial = cabeza
            for alternativa in resto.split('|'):
                simbolos = alternativa.split()
                if not simbolos:
                    raise ValueError(f'línea {n}: alternativa vacía, usa e para épsilon')
                cuerpo = tuple(s for s in simbolos if s not in VACIOS)
                agregar(producciones, cabeza, cuerpo)
    if inicial is None:
        raise ValueError('el archivo no tiene producciones')
    return Gramatica(inicial, producciones)


def guardar(g, ruta):
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(str(g).replace(EPS, 'e') + '\n')
