# ============================================================
# FIND FILTER CONTAINER STABLE
# ============================================================
#
# OBJETIVO
# --------
# Encontrar filtros REALES del panel lateral
# después de CADA rerender Power BI.
#
# SOLUCIÓN DEFINITIVA
# -------------------
# Ya NO:
#   - índices persistentes
#   - nth() fijo
#   - matching global
#
# Ahora:
#   - remap containers
#   - filtrar comboboxes reales
#   - matching semántico
#
# ============================================================

def find_filter_container_stable(
    page,
    label
):

    section(
        f"FIND FILTER STABLE -> {label}"
    )

    #
    # MUY IMPORTANTE
    #
    # Re-mapear DESPUÉS de cada rerender.
    #
    # Power BI:
    # - reconstruye DOM
    # - recicla containers
    # - cambia índices
    #

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"TOTAL CONTAINERS: {total}")

    candidates = []

    # ========================================================
    # ITERAR CONTAINERS
    # ========================================================

    for i in range(total):

        try:

            container = containers.nth(i)

            # ------------------------------------------------
            # SOLO containers con combobox
            # ------------------------------------------------

            combos = container.locator(
                "[role='combobox']"
            )

            combo_count = combos.count()

            if combo_count == 0:
                continue

            # ------------------------------------------------
            # TEXTO
            # ------------------------------------------------

            try:

                text = container.inner_text(
                    timeout=2000
                )

            except:
                continue

            text = text.strip()

            print("\n")
            print("-" * 60)

            print(f"INDEX: {i}")

            print(f"COMBOBOXES: {combo_count}")

            print("\nTEXT:\n")

            print(text[:400])

            # ------------------------------------------------
            # MATCH SEMÁNTICO
            # ------------------------------------------------

            if label.lower() in text.lower():

                print("\nMATCH FOUND")

                candidates.append({

                    "index": i,
                    "container": container,
                    "text": text

                })

        except Exception as e:

            print(f"ERROR INDEX {i}: {e}")

    # ========================================================
    # VALIDACIÓN
    # ========================================================

    if len(candidates) == 0:

        raise Exception(
            f"No filter found: {label}"
        )

    #
    # Si hubiera múltiples matches,
    # usar el primero.
    #
    # Normalmente será único.
    #

    target = candidates[0]

    print("\n")
    print("=" * 80)

    print("FINAL FILTER SELECTED")

    print("=" * 80)

    print(f"INDEX: {target['index']}")

    print("\nTEXT:\n")

    print(target["text"][:500])

    return target["container"]