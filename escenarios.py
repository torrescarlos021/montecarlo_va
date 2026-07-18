"""
Análisis de escenarios — dimensionamiento de la Ruta de Salud Arriaga
El modelo base (1 unidad, 2 jornadas/semana) resultó insuficiente.
Se evalúan configuraciones alternativas.
"""
import numpy as np
rng = np.random.default_rng(42)
N = 10_000

poblacion_objetivo = rng.triangular(2760, 4500, 7119, N)
consultas_por_persona = rng.triangular(1.5, 2.2, 3.0, N)
gasto_evitado_consulta = rng.triangular(150, 280, 450, N)


def escenario(nombre, n_unidades, jornadas_sem, semanas=48,
              consultas_jornada_media=28, frac_promotores=0.0):
    disponibilidad = rng.beta(18, 2, N)
    consultas_por_jornada = rng.normal(consultas_jornada_media, 5, N).clip(10, 50)
    tasa_asistencia = rng.beta(6, 4, N)

    jornadas = n_unidades * jornadas_sem * semanas * disponibilidad
    capacidad = jornadas * consultas_por_jornada

    demanda = poblacion_objetivo * tasa_asistencia * consultas_por_persona
    # Los promotores comunitarios resuelven una fracción del seguimiento
    demanda_unidad = demanda * (1 - frac_promotores)

    entregadas_unidad = np.minimum(capacidad, demanda_unidad)
    entregadas_promotor = demanda * frac_promotores
    entregadas = entregadas_unidad + entregadas_promotor

    personas = entregadas / consultas_por_persona
    cobertura = (personas / poblacion_objetivo) * 100
    gasto = entregadas * gasto_evitado_consulta

    print(f"\n{'='*72}")
    print(f"  {nombre}")
    print(f"{'='*72}")
    print(f"  Configuración: {n_unidades} unidad(es) x {jornadas_sem} jornada(s)/semana"
          f"{f' + promotores ({frac_promotores:.0%} del seguimiento)' if frac_promotores else ''}")
    print(f"  Consultas entregadas/año : {np.median(entregadas):>8,.0f}  "
          f"[P5 {np.percentile(entregadas,5):,.0f} – P95 {np.percentile(entregadas,95):,.0f}]")
    print(f"  Personas cubiertas       : {np.median(personas):>8,.0f}  "
          f"[P5 {np.percentile(personas,5):,.0f} – P95 {np.percentile(personas,95):,.0f}]")
    print(f"  Cobertura efectiva       : {np.median(cobertura):>7.1f}%  "
          f"[P5 {np.percentile(cobertura,5):.1f}% – P95 {np.percentile(cobertura,95):.1f}%]")
    print(f"  Gasto de bolsillo evitado: ${np.median(gasto):>9,.0f} MXN/año")
    print(f"  P(cobertura >= 60%)      : {(cobertura>=60).mean()*100:>7.1f}%")
    print(f"  P(cobertura >= 70%)      : {(cobertura>=70).mean()*100:>7.1f}%")
    print(f"  P(cobertura >= 80%)      : {(cobertura>=80).mean()*100:>7.1f}%")
    return cobertura, gasto


print("\n" + "#"*72)
print("#  ANÁLISIS DE ESCENARIOS — DIMENSIONAMIENTO DE LA INTERVENCIÓN")
print("#"*72)

escenario("ESCENARIO A — Configuración inicial (piloto mínimo)", 1, 2)
escenario("ESCENARIO B — Ampliación de flota", 2, 3)
escenario("ESCENARIO C — Unidad + red de promotores comunitarios", 1, 3,
          frac_promotores=0.45)
cob_d, gasto_d = escenario("ESCENARIO D — 2 unidades + red de promotores (propuesta final)",
                           2, 3, frac_promotores=0.45)

print("\n" + "="*72)
print("  CONCLUSIÓN DEL DIMENSIONAMIENTO")
print("="*72)
print(f"  El Escenario D alcanza una cobertura mediana de {np.median(cob_d):.1f}%")
print(f"  con una probabilidad de {(cob_d>=70).mean()*100:.1f}% de superar el 70%.")
print(f"  Protección financiera mediana: ${np.median(gasto_d):,.0f} MXN/año")
print("="*72)
