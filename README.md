# Ruta de Salud Arriaga

**Modelo de simulación Monte Carlo para el dimensionamiento de una intervención de cobertura sanitaria universal en Villa de Arriaga, San Luis Potosí.**

Meta 3.8 del Objetivo de Desarrollo Sostenible 3 — *Salud y bienestar*.

---

## ¿Qué es esto?

Villa de Arriaga es un municipio del altiplano potosino donde 2,760 personas usan el consultorio de farmacia como su principal opción de atención médica (INEGI, 2020). No es que no busquen atención: la pagan de su bolsillo porque el sistema público no las alcanza. Eso es, en los términos exactos de la meta 3.8, una falla de cobertura.

Este repositorio contiene el modelo probabilístico que se usó para **dimensionar** una propuesta de solución —una red itinerante de atención primaria con telemedicina y promotores comunitarios— antes de comprometer un solo peso de recurso público.

La pregunta que responde el modelo no es *"¿funcionaría?"*, sino **"¿con qué probabilidad, y qué configuración se necesita para lograrlo?"**

## ¿Por qué Monte Carlo?

Porque un plan de salud pública construido sobre promedios miente. La asistencia a una jornada médica no es "60%": es una distribución. La disponibilidad de una unidad móvil no es "siempre": depende del clima, del mantenimiento y del camino. Un modelo determinista entrega un número que suena preciso y que nunca se cumple.

Monte Carlo trata cada variable como una distribución de probabilidad, corre el sistema 10,000 veces y entrega un **rango con probabilidades asociadas**. En lugar de "atenderemos a 2,800 personas", se puede afirmar: *"la cobertura mediana es 60.9%, con 52.3% de probabilidad de alcanzar la meta y un piso razonable (P5) de 34.3%"*. Eso es un pronóstico, no una promesa.

## Resultados

El hallazgo más importante del modelo fue **negativo**, y obligó a rediseñar la propuesta original.

| Escenario | Configuración | Cobertura mediana | P(cobertura ≥ 60%) |
|-----------|---------------|:-----------------:|:------------------:|
| A | 1 unidad, 2 jornadas/semana | 22.9 % | 0.0 % |
| B | 2 unidades, 3 jornadas/semana | 54.6 % | 34.6 % |
| C | 1 unidad + red de promotores | 56.3 % | 38.6 % |
| **D** | **2 unidades + red de promotores** | **60.9 %** | **52.3 %** |

**Dos conclusiones que el modelo reveló y la intuición no:**

1. **Los promotores comunitarios rinden más que un segundo vehículo.** El Escenario C, con la mitad de la flota del Escenario B, lo supera. Formar a la comunidad es más costo-efectivo que comprar equipo.

2. **Una vez resuelta la capacidad, el cuello de botella se mueve a la asistencia.** El análisis de sensibilidad muestra que la configuración inicial estaba limitada por *capacidad*; en la configuración final, la variable limitante pasa a ser la *tasa de asistencia*. Traducción: ampliar la oferta es necesario pero insuficiente si no se trabaja simultáneamente sobre los determinantes sociales que sostienen la barrera.

Escenario D (propuesta final):

- Cobertura efectiva: **60.9 %** (P5 = 34.3 % · P95 = 82.7 %)
- Consultas entregadas al año: ~6,180
- Gasto de bolsillo evitado: **$1,783,713 MXN / año** (mediana)

![Resultados de la simulación](figuras_montecarlo.png)

## Parámetros y sus fuentes

Ningún parámetro es inventado. Cada distribución está acotada por datos oficiales o por rangos operativos justificables.

| Parámetro | Distribución | Valores | Fuente / justificación |
|---|---|---|---|
| Población objetivo | Triangular | (2760, 4500, 7119) | Piso: personas que usan consultorio de farmacia (INEGI, 2020). Techo: 39.1 % de 18,206 hab., carencia nacional por acceso a servicios de salud (CONEVAL, 2022). |
| Tasa de asistencia | Beta(6, 4) | media ≈ 0.60 | Acotada en [0,1] y asimétrica. Refleja barreras de distancia, jornada laboral y desconfianza. |
| Consultas por jornada | Normal(28, 5) | recorte [10, 45] | Capacidad operativa de una unidad móvil con un médico general. |
| Disponibilidad de la unidad | Beta(18, 2) | media ≈ 0.90 | Fallas mecánicas, clima y mantenimiento en caminos de terracería. |
| Consultas por persona / año | Triangular | (1.5, 2.2, 3.0) | Seguimiento de pacientes crónicos en control. |
| Gasto evitado por consulta | Triangular | (150, 280, 450) MXN | Costo típico de consulta en consultorio adyacente a farmacia + medicamento. |
| Cobertura de conectividad | Beta(7, 3) | media ≈ 0.70 | Limita el componente de teleconsulta. |

### ¿Por qué esas distribuciones?

- **Triangular** cuando se conocen cotas duras (mínimo, máximo) y un valor más probable, pero no la forma exacta de la distribución. Es el caso de la población objetivo: hay un piso y un techo documentados.
- **Beta** para proporciones acotadas en [0, 1] que no son simétricas — asistencia, disponibilidad, conectividad.
- **Normal truncada** para la capacidad por jornada, que varía alrededor de un valor central por causas múltiples e independientes.

## Cómo correrlo

```bash
git clone https://github.com/<tu-usuario>/ruta-salud-arriaga.git
cd ruta-salud-arriaga
pip install -r requirements.txt

python montecarlo_villa_arriaga.py   # modelo base + sensibilidad + gráficas
python escenarios.py                 # comparación de las 4 configuraciones
python figuras.py                    # genera figuras_montecarlo.png
```

La semilla está fijada (`default_rng(42)`), así que los resultados son reproducibles exactamente. Cámbiala para verificar que las conclusiones son robustas y no un artefacto del muestreo.


## Cómo modificar el modelo

El modelo está pensado para ser cuestionado. Los puntos naturales de intervención:

- **Cambiar la población objetivo** → ajusta `rng.triangular(2760, 4500, 7119, N_SIM)` si consigues datos municipales más recientes.
- **Cambiar la escala de la intervención** → en `escenarios.py`, los parámetros `n_unidades`, `jornadas_sem` y `frac_promotores`.
- **Aplicarlo a otro municipio** → sustituye las cotas de población objetivo por las del municipio en cuestión. La estructura del modelo es la misma para cualquier localidad rural dispersa.

## Limitaciones

Vale la pena ser explícito sobre lo que este modelo **no** hace:

- No modela costos de operación ni retorno de inversión; estima gasto de bolsillo evitado, que es una medida de protección financiera, no un análisis costo-beneficio.
- La tasa de asistencia es el parámetro con mayor incertidumbre y sin anclaje empírico local. Debería calibrarse con datos reales tras el piloto.
- Supone una demanda estable a lo largo del año, sin estacionalidad.
- No modela la calidad clínica de la atención, solo el volumen y el alcance.

## Contexto académico

Desarrollado como parte de la Evidencia 1 de la materia **Salud Global para Líderes**, Tecnológico de Monterrey, Campus San Luis Potosí.

## Cómo citar

```
Torres Rosas, C. J. (2026). Ruta de Salud Arriaga: modelo de simulación
Monte Carlo para la meta 3.8 del ODS 3 (Versión 1.0) [Código fuente].
GitHub. https://github.com/<tu-usuario>/ruta-salud-arriaga
```

## Referencias de los datos

- Consejo Nacional de Evaluación de la Política de Desarrollo Social. (2013). *Informe anual sobre la situación de pobreza y rezago social 2013: Villa de Arriaga, San Luis Potosí*.
- Consejo Nacional de Evaluación de la Política de Desarrollo Social. (2023). *Medición multidimensional de la pobreza en México, 2018-2022*.
- Instituto Nacional de Estadística y Geografía. (2021). *Censo de Población y Vivienda 2020: panorama sociodemográfico de Villa de Arriaga, San Luis Potosí*.
- Kruk, M. E., Gage, A. D., Joseph, N. T., Danaei, G., García-Saisó, S., & Salomon, J. A. (2018). Mortality due to low-quality health systems in the universal health coverage era. *The Lancet, 392*(10160), 2203–2212.

## Licencia

MIT
