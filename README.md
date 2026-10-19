# Proyecto 2 – CYK

Teoría de la Computación, UVG

- Samuel Robledo – 241282

Repositorio: https://github.com/samuelrobledo52/Proyecto2-TC
Video: (link)

## Descripción

Lee una gramática libre de contexto, la convierte a Forma Normal de Chomsky y valida frases con CYK. Por cada frase muestra SÍ o NO, el tiempo, la tabla y el parse tree. La gramática puede venir ya en CNF.

## Archivos

- `main.py`: lee la gramática y las frases y muestra los resultados.
- `gramatica.py`: lectura del archivo y clase `Gramatica`.
- `cnf.py`: elimina ε, unitarias e inútiles y pasa a CNF.
- `cyk.py`: algoritmo CYK y tabla.
- `arbol.py`: parse tree en texto y en imagen.
- `gramaticas/`: `ingles.txt`, `1.txt`, `1-cnf.txt` y `prueba.txt`.
- `pruebas/equivalencia.py`: compara la gramática original contra la CNF.

## Formato de la gramática

Una producción por línea, símbolos separados por espacios, `|` para alternativas y `e` para épsilon. La primera cabeza es el símbolo inicial.

## Uso

Solo usa Python estándar. Las imágenes necesitan Graphviz (`dot`).

```
python main.py gramaticas/ingles.txt "She eats a cake with a fork"
python main.py gramaticas/ingles.txt -f frases_ingles.txt
python main.py gramaticas/1.txt -f frases_expresiones.txt -o salida_expr
```

Sin frase, el programa las pide por consola. Los resultados se guardan en `salida/`.

## Ejemplos

- Sí: `She eats a cake with a fork`, `The cat drinks the beer`, `(id*id)+id`.
- No: `she eats cake`, `the dog eats with a fork the soup`, `(id*id`.

---

Se utilizó Claude como apoyo en la implementación y la documentación. Todo el contenido fue revisado, probado y validado por mí.
