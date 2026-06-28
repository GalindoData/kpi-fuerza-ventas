import pandas as pd
import numpy as np


def generar_datos_ejecutivos(seed: int = 42) -> pd.DataFrame:
    """
    Genera datos simulados de fuerza de ventas bancaria.

    Args:
        seed: semilla para reproducibilidad de los datos aleatorios.

    Returns:
        DataFrame con métricas mensuales por ejecutivo.
    """
    rng = np.random.default_rng(seed)

    regiones = ["Norte", "Centro", "Sur", "CDMX", "Occidente"]
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
    nombres = [
        "García",
        "López",
        "Martínez",
        "Hernández",
        "González",
        "Pérez",
        "Rodríguez",
        "Sánchez",
        "Ramírez",
        "Torres",
        "Flores",
        "Rivera",
        "Gómez",
        "Díaz",
        "Cruz",
        "Morales",
        "Reyes",
        "Gutiérrez",
        "Ortiz",
        "Mendoza",
        "Castillo",
        "Jiménez",
        "Vargas",
        "Romero",
        "Navarro",
        "Ramos",
        "Domínguez",
        "Vega",
        "Serrano",
        "Molina",
        "Ruiz",
        "Moreno",
        "Suárez",
        "Aguilar",
        "Muñoz",
        "Medina",
        "Guerrero",
        "Paredes",
        "Luna",
        "Campos",
    ]

    registros = []

    for i, apellido in enumerate(nombres):
        region = regiones[i % len(regiones)]
        meta_base = int(rng.integers(800_000, 2_000_000))

        for mes in meses:
            cumplimiento = rng.normal(loc=0.92, scale=0.15)
            cumplimiento = max(0.4, min(1.4, cumplimiento))

            registros.append(
                {
                    "ejecutivo_id": f"EJC-{i+1:03d}",
                    "nombre": f"Ejecutivo {apellido}",
                    "region": region,
                    "mes": mes,
                    "meta_mxn": meta_base,
                    "venta_real_mxn": round(meta_base * cumplimiento),
                    "clientes_nuevos": int(max(0, rng.normal(loc=8, scale=3))),
                    "productos_colocados": int(max(0, rng.normal(loc=12, scale=4))),
                }
            )

    df = pd.DataFrame(registros)
    df["cumplimiento_pct"] = (df["venta_real_mxn"] / df["meta_mxn"] * 100).round(1)
    return df


if __name__ == "__main__":
    df = generar_datos_ejecutivos()
    df.to_csv("data/ejecutivos.csv", index=False)
    print(f"  Datos generados: {len(df)} registros")
    print(f"  Ejecutivos: {df['ejecutivo_id'].nunique()}")
    print(f"  Meses: {df['mes'].nunique()}")
    print(df.head())
