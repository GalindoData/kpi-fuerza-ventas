import pandas as pd
import numpy as np
from generar_datos import generar_datos_ejecutivos


def cargar_datos(ruta: str = "data/ejecutivos.csv") -> pd.DataFrame:
    """
    Carga y valida el dataset de ejecutivos.

    Args:
        ruta: path al archivo CSV.

    Returns:
        DataFrame validado con los datos de ejecutivos.
    """
    df = pd.read_csv(ruta)

    columnas_requeridas = {
        "ejecutivo_id",
        "nombre",
        "region",
        "mes",
        "meta_mxn",
        "venta_real_mxn",
        "clientes_nuevos",
        "productos_colocados",
        "cumplimiento_pct",
    }

    faltantes = columnas_requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Columnas faltantes en el dataset: {faltantes}")

    return df


def kpis_por_ejecutivo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolida métricas acumuladas por ejecutivo para el período completo.

    Args:
        df: DataFrame con datos mensuales de ejecutivos.

    Returns:
        DataFrame con KPIs agregados, ranking y semáforo por ejecutivo.
    """
    resumen = (
        df.groupby(["ejecutivo_id", "nombre", "region"])
        .agg(
            meta_total=("meta_mxn", "sum"),
            venta_total=("venta_real_mxn", "sum"),
            clientes_total=("clientes_nuevos", "sum"),
            productos_total=("productos_colocados", "sum"),
        )
        .reset_index()
    )

    resumen["cumplimiento_pct"] = (
        resumen["venta_total"] / resumen["meta_total"] * 100
    ).round(1)

    def clasificar_semaforo(cumplimiento: float) -> str:
        if cumplimiento >= 95:
            return "Verde"
        elif cumplimiento >= 80:
            return "Amarillo"
        else:
            return "Rojo"

    resumen["semaforo"] = resumen["cumplimiento_pct"].apply(clasificar_semaforo)

    resumen["ranking_global"] = (
        resumen["cumplimiento_pct"].rank(ascending=False, method="dense").astype(int)
    )

    return resumen.sort_values("cumplimiento_pct", ascending=False).reset_index(
        drop=True
    )


def kpis_por_region(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolida métricas por región para análisis de capilaridad.

    Args:
        df: DataFrame con datos mensuales de ejecutivos.

    Returns:
        DataFrame con KPIs agregados por región.
    """
    resumen = (
        df.groupby("region")
        .agg(
            ejecutivos=("ejecutivo_id", "nunique"),
            meta_total=("meta_mxn", "sum"),
            venta_total=("venta_real_mxn", "sum"),
            clientes_total=("clientes_nuevos", "sum"),
            productos_total=("productos_colocados", "sum"),
        )
        .reset_index()
    )

    resumen["cumplimiento_pct"] = (
        resumen["venta_total"] / resumen["meta_total"] * 100
    ).round(1)

    resumen["venta_por_ejecutivo"] = (
        resumen["venta_total"] / resumen["ejecutivos"]
    ).round(0)

    return resumen.sort_values("cumplimiento_pct", ascending=False)


if __name__ == "__main__":
    df = cargar_datos()
    print("\n── KPIs por Ejecutivo (Top 10) ──")
    resumen = kpis_por_ejecutivo(df)
    print(
        resumen[
            ["nombre", "region", "cumplimiento_pct", "semaforo", "ranking_global"]
        ].head(10)
    )
    print("\n── KPIs por Región ──")
    print(kpis_por_region(df).to_string(index=False))
