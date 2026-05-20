import sympy as sp

# =====================================
# CONFIGURACIÓN GLOBAL
# =====================================

x = sp.symbols('x')

print("\n========================================")
print(" CALCULADORA UNIVERSAL DE MACLAURIN")
print("========================================")
print("Puede ingresar cualquier función simbólica.")
print("Ejemplos:")
print("exp(x)*sin(x)")
print("log(1+x)")
print("(x**2+1)/(1-x)")
print("sqrt(1+x)")
print("sin(x**2)+cos(x)")
print("----------------------------------------")

# =====================================
# FUNCIÓN SEGURA PARA LEER EXPRESIONES
# =====================================

def leer_funcion():
    while True:
        try:
            texto = input("\nIngrese f(x): ")

            # Conversión segura a expresión simbólica
            f = sp.sympify(
                texto,
                locals={
                    "x": x,
                    "sin": sp.sin,
                    "cos": sp.cos,
                    "tan": sp.tan,
                    "exp": sp.exp,
                    "log": sp.log,
                    "sqrt": sp.sqrt,
                    "asin": sp.asin,
                    "acos": sp.acos,
                    "atan": sp.atan,
                    "sinh": sp.sinh,
                    "cosh": sp.cosh,
                    "tanh": sp.tanh,
                    "pi": sp.pi,
                    "E": sp.E
                }
            )

            return sp.simplify(f)

        except Exception as e:
            print("❌ Expresión inválida:", e)

# =====================================
# LEER DATOS
# =====================================

f = leer_funcion()

while True:
    try:
        n = int(input("Orden de aproximación n: "))
        if n <= 0:
            raise ValueError
        break
    except:
        print("❌ Ingrese un entero positivo.")

# =====================================
# CÁLCULO GENERAL DE MACLAURIN
# =====================================

try:
    serie = sp.series(f, x, 0, n+1).removeO()
except:
    print("\n⚠ No se pudo calcular la serie automáticamente.")
    exit()

# =====================================
# RESULTADOS
# =====================================

print("\n========== RESULTADOS ==========")

print("\nFunción original:")
sp.pprint(f)

print("\nSerie de Maclaurin:")
sp.pprint(sp.expand(serie))

# =====================================
# ERROR NUMÉRICO OPCIONAL
# =====================================

op = input("\n¿Evaluar aproximación? (s/n): ")

if op.lower() == "s":
    try:
        valor = float(input("Valor de x: "))

        real = sp.N(f.subs(x, valor))
        aprox = sp.N(serie.subs(x, valor))

        print("\nValor real =", real)
        print("Aproximación =", aprox)
        print("Error absoluto =", abs(real - aprox))

    except:
        print("❌ No se pudo evaluar.")

print("\nPrograma finalizado.")