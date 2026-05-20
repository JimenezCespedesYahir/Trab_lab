import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

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
serie = None # Initialize serie
try:
    serie = sp.series(f, x, 0, n+1).removeO()
except Exception as e: # Catch specific exception if possible, or general Exception
    print(f"\n⚠ No se pudo calcular la serie automáticamente: {e}")
    # Don't exit, just continue. Subsequent blocks will check if serie is None.

if serie is None:
    print("\nPrograma finalizado debido a un error en el cálculo de la serie.")
else:
    # =====================================
    # RESULTADOS
    # =====================================

    print("\n========== RESULTADOS ==========")

    print("\nFunción original:")
    sp.pprint(f)

    print("\nSerie de Maclaurin:")
    sp.pprint(sp.expand(serie))

    # =====================================
    # RADIO DE CONVERGENCIA
    # =====================================
    print("\n========== RADIO DE CONVERGENCIA ==========")

    R_val = None # Initialize R_val
    try:
        singularities = sp.singularities(f, x)

        if not singularities:
            R_val = sp.oo
            print("Radio de Convergencia (R): ∞ (infinito)")
        else:
            numeric_distances = []
            for s in singularities:
                try:
                    # Evaluate absolute value of complex singularity numerically
                    distance = sp.N(abs(s))
                    if sp.is_finite(distance): # Ensure distance is a finite number
                        numeric_distances.append(float(distance))
                except Exception:
                    # Skip if evaluation fails (e.g., symbolic singularity that can't be resolved)
                    continue

            if numeric_distances:
                min_abs_distance = min(numeric_distances)
                R_val = min_abs_distance
                print(f"Radio de Convergencia (R): {R_val:.4f}")
            else:
                # No numerical singularities found, possibly all symbolic or issues
                R_val = sp.oo # Assume infinite if no limiting singularity found
                print("No se encontraron singularidades numéricas que limiten el Radio de Convergencia. Asumiendo R: ∞ (infinito)")

    except Exception as e:
        print(f"No se pudo calcular el Radio de Convergencia automáticamente: {e}")
        print("Para funciones como exp(x), sin(x), cos(x), el radio es infinito.")
        print("Para funciones como 1/(1-x) o log(1+x), el radio es 1.")

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

        except Exception as e: # Catch any evaluation error
            print(f"❌ No se pudo evaluar: {e}")

    # =====================================
    # GRÁFICA DE LA APROXIMACIÓN
    # =====================================
    print("\n========== GRÁFICA ==========")

    try:
        # Convert sympy expressions to numpy-compatible functions
        f_numeric = sp.lambdify(x, f, 'numpy')
        serie_numeric = sp.lambdify(x, serie, 'numpy')

        # Determine plotting range based on Radius of Convergence
        if R_val is sp.oo or R_val is None:
            plot_range = 5.0  # Default range if R is infinite or not calculated
        else:
            plot_range = float(R_val) * 1.5 # Extend slightly beyond R for better visualization
            if plot_range == 0.0: # Avoid issues if R is calculated as 0
                plot_range = 1.0
            if plot_range > 20.0: # Cap the plot range for very large R for practical visualization
                plot_range = 20.0

        x_vals = np.linspace(-plot_range, plot_range, 400)

        # Evaluate functions. Handle potential issues with lambdified functions.
        try:
            y_original = f_numeric(x_vals)
            y_approx = serie_numeric(x_vals)
        except Exception as e:
            print(f"Error al evaluar las funciones para la gráfica: {e}")
            print("Puede que la función no esté definida en todo el rango de x o que la serie sea muy compleja.")
            raise # Re-raise to trigger the outer catch for plotting

        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_original, label='Función Original f(x)', color='blue')
        plt.plot(x_vals, y_approx, label=f'Serie de Maclaurin (orden {n})', color='red', linestyle='--')

        plt.title(f'Aproximación de Maclaurin para f(x) = {f}')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.grid(True)
        plt.axvline(0, color='gray', linestyle='--', linewidth=0.7)
        plt.axhline(0, color='gray', linestyle='--', linewidth=0.7)

        # Indicate Radius of Convergence if finite and non-zero
        if R_val is not sp.oo and R_val is not None and R_val > 0:
            plt.axvline(-float(R_val), color='green', linestyle=':', label=f'Radio de Convergencia R={float(R_val):.2f}')
            plt.axvline(float(R_val), color='green', linestyle=':')
            plt.legend()

        # Adjust y-limits dynamically, handle potential for constant functions or infinite values
        y_min_val = np.min(y_original[np.isfinite(y_original)])
        y_max_val = np.max(y_original[np.isfinite(y_original)])

        if not np.isfinite(y_min_val) or not np.isfinite(y_max_val): # If original function contains infinite values
            plt.ylim(-5, 5) # Default fixed range
        elif np.isclose(y_min_val, y_max_val): # If function is constant
            plt.ylim(y_min_val - 1, y_max_val + 1)
        else:
            # Add some padding to y-limits
            padding = (y_max_val - y_min_val) * 0.1
            plt.ylim(y_min_val - padding, y_max_val + padding)


        plt.show()

    except Exception as e:
        print(f"No se pudo generar la gráfica: {e}")

    print("\nPrograma finalizado.")