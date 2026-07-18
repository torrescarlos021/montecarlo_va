"""
Modelo de simulación Monte Carlo
Propuesta: "Ruta de Salud Arriaga" - Unidad móvil con telemedicina
Meta ODS 3.8 (Cobertura Sanitaria Universal) - Villa de Arriaga, S.L.P.

Autor: Carlos Torres | Salud Global para Líderes | Tec de Monterrey

Parámetros anclados en:
- INEGI (2020): población municipal 18,206 hab.
- Data México / INEGI (2020): 2,760 personas usan consultorio de farmacia
  como principal opción de atención (proxy de gasto de bolsillo).
- CONEVAL (2022): carencia nacional por acceso a servicios de salud = 39.1%
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
N_SIM = 10_000

# ----------------------------------------------------------------------
# 1. PARÁMETROS DE ENTRADA (distribuciones de incertidumbre)
# ----------------------------------------------------------------------

# Población objetivo: personas sin acceso efectivo a servicios de salud.
# Cota inferior: 2,760 (usuarios de consultorio de farmacia, INEGI 2020)
# Cota superior: 39.1% de 18,206 = 7,119 (carencia nacional, CONEVAL 2022)
# Moda: 4,500 (estimación intermedia)
poblacion_objetivo = rng.triangular(2760, 4500, 7119, N_SIM)

# Jornadas operativas al año (2 salidas/semana x 48 semanas = 96)
# Se modela variabilidad por clima, mantenimiento y días festivos
jornadas_programadas = 96
disponibilidad = rng.beta(18, 2, N_SIM)          # media ~0.90
jornadas_efectivas = jornadas_programadas * disponibilidad

# Consultas atendidas por jornada (capacidad operativa de la unidad)
consultas_por_jornada = rng.normal(28, 5, N_SIM).clip(10, 45)

# Tasa de asistencia: proporción de la población convocada que sí acude
# (barreras: distancia, jornada laboral, desconfianza, desinformación)
tasa_asistencia = rng.beta(6, 4, N_SIM)          # media ~0.60

# Consultas por persona al año (seguimiento de crónicos, control)
consultas_por_persona = rng.triangular(1.5, 2.2, 3.0, N_SIM)

# Gasto de bolsillo evitado por consulta (consulta de farmacia + medicamento)
# Rango basado en costo típico de consultorio adyacente a farmacia en México
gasto_evitado_consulta = rng.triangular(150, 280, 450, N_SIM)

# Cobertura de conectividad para teleconsulta (limita el componente remoto)
cobertura_conectividad = rng.beta(7, 3, N_SIM)   # media ~0.70

# ----------------------------------------------------------------------
# 2. MODELO
# ----------------------------------------------------------------------

# Capacidad máxima anual del sistema
capacidad_anual = jornadas_efectivas * consultas_por_jornada

# Demanda real que acude
demanda_potencial = poblacion_objetivo * tasa_asistencia * consultas_por_persona

# Consultas efectivamente entregadas = mínimo entre capacidad y demanda
consultas_entregadas = np.minimum(capacidad_anual, demanda_potencial)

# Personas únicas cubiertas
personas_cubiertas = consultas_entregadas / consultas_por_persona

# Cobertura efectiva (% de la población objetivo alcanzada)
cobertura_efectiva = (personas_cubiertas / poblacion_objetivo) * 100

# Gasto de bolsillo evitado al año (protección financiera, meta 3.8)
gasto_evitado_total = consultas_entregadas * gasto_evitado_consulta

# Teleconsultas resueltas sin traslado a la capital
teleconsultas = consultas_entregadas * cobertura_conectividad * 0.35

# ----------------------------------------------------------------------
# 3. RESULTADOS
# ----------------------------------------------------------------------

def resumen(nombre, arr, unidad="", dec=0):
    p5, p50, p95 = np.percentile(arr, [5, 50, 95])
    print(f"{nombre:<42} media={arr.mean():>10,.{dec}f} {unidad}")
    print(f"{'':<42} P5={p5:>12,.{dec}f}  P50={p50:>10,.{dec}f}  P95={p95:>10,.{dec}f}")
    print()

print("=" * 78)
print("SIMULACIÓN MONTE CARLO — RUTA DE SALUD ARRIAGA")
print(f"{N_SIM:,} iteraciones | Horizonte: 12 meses de operación")
print("=" * 78)
print()

resumen("Población objetivo (personas)", poblacion_objetivo)
resumen("Jornadas efectivas al año", jornadas_efectivas, dec=1)
resumen("Consultas entregadas al año", consultas_entregadas)
resumen("Personas únicas cubiertas", personas_cubiertas)
resumen("Cobertura efectiva (%)", cobertura_efectiva, "%", dec=1)
resumen("Gasto de bolsillo evitado (MXN/año)", gasto_evitado_total)
resumen("Teleconsultas sin traslado", teleconsultas)

print("-" * 78)
print("PROBABILIDAD DE ALCANZAR METAS DE COBERTURA")
print("-" * 78)
for meta in [40, 50, 60, 70, 80]:
    p = (cobertura_efectiva >= meta).mean() * 100
    print(f"  P(cobertura efectiva >= {meta}%)  =  {p:5.1f}%")
print()

print("-" * 78)
print("PROBABILIDAD DE PROTECCIÓN FINANCIERA")
print("-" * 78)
for meta in [500_000, 750_000, 1_000_000]:
    p = (gasto_evitado_total >= meta).mean() * 100
    print(f"  P(gasto de bolsillo evitado >= ${meta:,} MXN)  =  {p:5.1f}%")
print()

# Análisis de sensibilidad (correlación de Spearman con la cobertura)
from scipy.stats import spearmanr
print("-" * 78)
print("ANÁLISIS DE SENSIBILIDAD (correlación con cobertura efectiva)")
print("-" * 78)
variables = {
    "Población objetivo": poblacion_objetivo,
    "Tasa de asistencia": tasa_asistencia,
    "Consultas por jornada": consultas_por_jornada,
    "Disponibilidad de la unidad": disponibilidad,
    "Consultas por persona/año": consultas_por_persona,
}
sens = []
for nom, var in variables.items():
    r, _ = spearmanr(var, cobertura_efectiva)
    sens.append((nom, r))
for nom, r in sorted(sens, key=lambda x: -abs(x[1])):
    barra = "#" * int(abs(r) * 40)
    print(f"  {nom:<30} r = {r:+.3f}  {barra}")
print()

# ----------------------------------------------------------------------
# 4. GRÁFICAS
# ----------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))

ax = axes[0]
ax.hist(cobertura_efectiva, bins=60, color="#2E86AB", edgecolor="white", alpha=.85)
p5, p50, p95 = np.percentile(cobertura_efectiva, [5, 50, 95])
ax.axvline(p50, color="#C0392B", lw=2, label=f"Mediana = {p50:.1f}%")
ax.axvline(p5, color="#7F8C8D", ls="--", lw=1.5, label=f"P5 = {p5:.1f}%")
ax.axvline(p95, color="#7F8C8D", ls="--", lw=1.5, label=f"P95 = {p95:.1f}%")
ax.set_xlabel("Cobertura efectiva de la población objetivo (%)")
ax.set_ylabel("Frecuencia (nº de simulaciones)")
ax.set_title("Figura 1. Distribución de la cobertura efectiva\n(10,000 simulaciones)",
             fontsize=10, fontweight="bold")
ax.legend(fontsize=8)
ax.spines[["top", "right"]].set_visible(False)

ax = axes[1]
ax.hist(gasto_evitado_total / 1000, bins=60, color="#27AE60", edgecolor="white", alpha=.85)
g50 = np.percentile(gasto_evitado_total, 50) / 1000
ax.axvline(g50, color="#C0392B", lw=2, label=f"Mediana = ${g50:,.0f}k MXN")
ax.set_xlabel("Gasto de bolsillo evitado (miles de MXN / año)")
ax.set_ylabel("Frecuencia (nº de simulaciones)")
ax.set_title("Figura 2. Protección financiera anual estimada\n(meta ODS 3.8)",
             fontsize=10, fontweight="bold")
ax.legend(fontsize=8)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("/home/claude/montecarlo_resultados.png", dpi=160, bbox_inches="tight")
print("Gráficas guardadas: montecarlo_resultados.png")
