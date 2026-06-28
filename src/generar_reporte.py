import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import base64
import io
from jinja2 import Template
from calcular_kpis import cargar_datos, kpis_por_ejecutivo, kpis_por_region


def fig_a_base64(fig) -> str:
    """
    Convierte una figura matplotlib a string base64 para incrustar en HTML.

    Args:
        fig: figura de matplotlib.

    Returns:
        String base64 de la imagen PNG.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img_b64


def grafica_cumplimiento_regional(df_region: pd.DataFrame) -> str:
    """
    Genera gráfica de barras horizontales de cumplimiento por región.

    Args:
        df_region: DataFrame con KPIs por región.
    Returns:
        String base64 de la imagen PNG.
    """
    colores = [
        "#2ecc71" if v >= 95 else "#f39c12" if v >= 80 else "#e74c3c"
        for v in df_region["cumplimiento_pct"]
    ]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    bars = ax.barh(df_region["region"], df_region["cumplimiento_pct"], color=colores)
    ax.axvline(x=95, color="#2ecc71", linestyle="--", linewidth=1, label="Meta (95%)")
    ax.axvline(x=80, color="#f39c12", linestyle="--", linewidth=1, label="Mínimo (80%)")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_xlabel("Cumplimiento %")
    ax.set_title("Cumplimiento de Meta por Región", fontweight="bold", pad=12)

    for bar, val in zip(bars, df_region["cumplimiento_pct"]):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%",
            va="center",
            fontsize=9,
        )
    fig.tight_layout()
    return fig_a_base64(fig)


def grafica_top10(df_ejec: pd.DataFrame) -> str:
    """
    Genera gráfica de Top 10 ejecutivos por cumplimiento.

    Args:
        df_ejec: DataFrame con KPIs por ejecutivo.

    Returns:
        String base64 de la imagen PNG.
    """
    top10 = df_ejec.head(10).copy()
    colores = [
        "#2ecc71" if v >= 95 else "#f39c12" if v >= 80 else "#e74c3c"
        for v in top10["cumplimiento_pct"]
    ]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(top10["nombre"], top10["cumplimiento_pct"], color=colores)
    ax.axvline(x=95, color="#2ecc71", linestyle="--", linewidth=1)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_title(
        "Top 10 Ejecutivos - Cumplimiento Acumulado", fontweight="bold", pad=12
    )
    ax.invert_yaxis()
    fig.tight_layout()
    return fig_a_base64(fig)


TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Reporte KPIs — Fuerza de Ventas</title>
<style>
  body { font-family: Arial, sans-serif; margin: 0; background: #f4f6f9; color: #2c3e50; }
  .header { background: #3aa2e8; color: white; padding: 28px 40px; }
  .header h1 { margin: 0; font-size: 22px; }
  .header p  { margin: 4px 0 0; font-size: 13px; opacity: 0.8; }
  .content { padding: 28px 40px; }
  .cards { display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }
  .card { background: white; border-radius: 8px; padding: 18px 24px;
          flex: 1; min-width: 160px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
  .card .num { font-size: 28px; font-weight: bold; color: #3aa2e8; }
  .card .lbl { font-size: 12px; color: #7f8c8d; margin-top: 4px; }
  .section { background: white; border-radius: 8px; padding: 20px 24px;
             margin-bottom: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
  .section h2 { margin: 0 0 16px; font-size: 15px; color: #3aa2e8;
                border-bottom: 2px solid #3aa2e8; padding-bottom: 8px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { background: #3aa2e8; color: white; padding: 8px 12px; text-align: left; }
  td { padding: 7px 12px; border-bottom: 1px solid #ecf0f1; }
  tr:hover td { background: #f8f9fa; }
  img { max-width: 100%; border-radius: 6px; }
  .footer { text-align: center; font-size: 11px; color: #95a5a6;
            padding: 20px; border-top: 1px solid #ecf0f1; margin-top: 8px; }
</style>
</head>
<body>

<div class="header">
  <h1>📊 Reporte de KPIs — Fuerza de Ventas Bancaria</h1>
  <p>Período: {{ periodo }} &nbsp;|&nbsp; Generado automáticamente con Python</p>
</div>

<div class="content">

  <div class="cards">
    <div class="card">
      <div class="num">{{ total_ejecutivos }}</div>
      <div class="lbl">Ejecutivos activos</div>
    </div>
    <div class="card">
      <div class="num">{{ cumplimiento_global }}%</div>
      <div class="lbl">Cumplimiento global</div>
    </div>
    <div class="card">
      <div class="num">{{ pct_verde }}%</div>
      <div class="lbl">En zona verde (≥95%)</div>
    </div>
    <div class="card">
      <div class="num">{{ pct_rojo }}%</div>
      <div class="lbl">En zona roja (&lt;80%)</div>
    </div>
    <div class="card">
      <div class="num">{{ clientes_total }}</div>
      <div class="lbl">Clientes nuevos totales</div>
    </div>
  </div>

  <div class="section">
    <h2>🗺️ Cumplimiento por Región</h2>
    <img src="data:image/png;base64,{{ grafica_regional }}" alt="Cumplimiento regional">
  </div>

  <div class="section">
    <h2>📋 Resumen por Región</h2>
    <table>
      <tr>
        <th>Región</th><th>Ejecutivos</th><th>Meta Total</th>
        <th>Venta Real</th><th>Cumplimiento</th><th>Venta/Ejecutivo</th>
      </tr>
      {% for _, r in df_region.iterrows() %}
      <tr>
        <td>{{ r.region }}</td>
        <td>{{ r.ejecutivos }}</td>
        <td>${{ "{:,.0f}".format(r.meta_total) }}</td>
        <td>${{ "{:,.0f}".format(r.venta_total) }}</td>
        <td>{{ r.cumplimiento_pct }}%</td>
        <td>${{ "{:,.0f}".format(r.venta_por_ejecutivo) }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <div class="section">
    <h2>🏆 Top 10 Ejecutivos</h2>
    <img src="data:image/png;base64,{{ grafica_top10 }}" alt="Top 10 ejecutivos">
  </div>

  <div class="section">
    <h2>👥 Detalle por Ejecutivo</h2>
    <table>
      <tr>
        <th>#</th><th>Ejecutivo</th><th>Región</th>
        <th>Cumplimiento</th><th>Clientes</th><th>Productos</th><th>Semáforo</th>
      </tr>
      {% for _, r in df_ejec.iterrows() %}
      <tr>
        <td>{{ r.ranking_global }}</td>
        <td>{{ r.nombre }}</td>
        <td>{{ r.region }}</td>
        <td>{{ r.cumplimiento_pct }}%</td>
        <td>{{ r.clientes_total }}</td>
        <td>{{ r.productos_total }}</td>
        <td>{{ r.semaforo }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>

</div>

<div class="footer">
  Reporte generado automáticamente · Sistema de Control de Gestión · Datos al {{ periodo }}
</div>

</body>
</html>
"""


def generar_reporte(
    ruta_datos: str = "data/ejecutivos.csv",
    ruta_salida: str = "output/reporte_kpis.html",
) -> None:
    """
    Pipeline completo: carga datos, calcula KPIs, genera reporte HTML.

    Args:
        ruta_datos: path al CSV de entrada.
        ruta_salida: path donde se guarda el HTML generado.
    """
    print("⏳ Cargando datos...")
    df = cargar_datos(ruta_datos)

    print("⏳ Calculando KPIs...")
    df_ejec = kpis_por_ejecutivo(df)
    df_region = kpis_por_region(df)

    print("⏳ Generando gráficas...")
    g_regional = grafica_cumplimiento_regional(df_region)
    g_top10 = grafica_top10(df_ejec)

    print("⏳ Calculando métricas globales...")
    total = len(df_ejec)
    cumplimiento_global = round(
        df_ejec["venta_total"].sum() / df_ejec["meta_total"].sum() * 100, 1
    )
    pct_verde = round(len(df_ejec[df_ejec["cumplimiento_pct"] >= 95]) / total * 100)
    pct_rojo = round(len(df_ejec[df_ejec["cumplimiento_pct"] < 80]) / total * 100)
    clientes_total = f"{df_ejec['clientes_total'].sum():,}"

    print("⏳ Ensamblando reporte HTML...")
    template = Template(TEMPLATE_HTML)
    html = template.render(
        periodo="Enero – Junio 2024",
        total_ejecutivos=total,
        cumplimiento_global=cumplimiento_global,
        pct_verde=pct_verde,
        pct_rojo=pct_rojo,
        clientes_total=clientes_total,
        df_region=df_region,
        df_ejec=df_ejec,
        grafica_regional=g_regional,
        grafica_top10=g_top10,
    )

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Reporte generado: {ruta_salida}")


if __name__ == "__main__":
    generar_reporte()
