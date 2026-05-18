# ADK Evaluator

Plantilla base para aprender a probar soluciones desarrolladas con Google ADK y evaluar ground truths y trayectorias. El proyecto está estructurado para ser escalable, modular y sencillo de extender.

## Características

- Modelos de dominio para ground truths, trayectorias y predicciones
- Evaluación de métricas de ruta, cobertura y coincidencia de etiquetas
- Capa de entrada/salida para JSON de datos de trayectorias
- Servicio de orquestación de evaluación con CLI simple
- Pruebas automatizadas con `pytest`

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .[dev]
```

## Uso

Ejecuta la evaluación con los archivos de ejemplo:

```powershell
.\.venv\Scripts\adk-evaluator --ground-truth data/sample_ground_truth.json --predictions data/sample_predictions.json --output results.json
```

Para ejecutar una evaluación con métricas ADK extendidas:

```powershell
.\.venv\Scripts\adk-evaluator --report-type adk --ground-truth data/sample_ground_truth.json --predictions data/sample_predictions.json --output results_adk.json
```

Este modo calcula métricas adicionales similares a las que usa una evaluación ADK real.

Si tus datos vienen en un formato de Google ADK, usa también `--input-format adk` junto con un adaptador de ejemplo:

```powershell
.\.venv\Scripts\adk-evaluator --report-type adk --input-format adk --ground-truth data/sample_adk_ground_truth.json --predictions data/sample_adk_predictions.json --output results_adk.json
```

Para una evaluación más completa, prueba el dataset extendido:

```powershell
.\.venv\Scripts\adk-evaluator --report-type adk --ground-truth data/sample_ground_truth_complex.json --predictions data/sample_predictions_complex.json --output results_complex_adk.json
```

## Estructura

- `src/adk_evaluator/`: código fuente principal
- `tests/`: pruebas unitarias
- `data/`: ejemplos de datos de ground truth y predicciones
- `docs/`: guía de arquitectura y pruebas

## Desarrollo

Este proyecto incluye varias capas de pruebas para asegurar que la base de evaluación funcione y sea fácil de extender.

### Qué tipos de pruebas tenemos

- `tests/test_models.py`
  - Validación de los modelos de dominio:
    - `Trajectory`
    - `TrajectoryPoint`
    - serialización/deserialización de datos
  - Útil para asegurar que los datos de entrada se representan correctamente.

- `tests/test_evaluation.py`
  - Validación de la lógica de evaluación básica:
    - cálculo de `path_error`
    - cálculo de `coverage`
    - comparación de etiquetas (`label_match`)
  - Usa ejemplos pequeños para comprobar que el evaluador funciona como se espera.

- `tests/test_io.py`
  - Validación de la capa de entrada/salida:
    - carga de ground truths
    - carga de predicciones
    - guardado de resultados JSON
  - Importante para garantizar que los archivos JSON se leen y escriben correctamente.

- `tests/test_integration.py`
  - Prueba el flujo completo de evaluación:
    - carga datos
    - ejecuta la evaluación
    - genera resultados en un archivo JSON
  - Es útil para comprobar que las piezas encajan entre sí.

- `tests/test_memory.py`
  - Prueba el componente de memoria del agente:
    - lecturas y escrituras
    - borrado de claves
    - merges y snapshots aislados
  - Usa casos unitarios para validar cómo se guarda y recupera el estado del agente.

- `tests/test_adk_evaluation.py`
  - Prueba el evaluador de métricas estilo ADK:
    - `precision`
    - `recall`
    - `f1_score`
    - `adk_score`
  - Permite verificar que la extensión ADK se calcula correctamente sobre el mismo flujo de trayectorias.

- `tests/test_adk_adapter.py`
  - Prueba la carga de datos en formato ADK, convirtiendo registros del estilo Google ADK en el modelo interno del proyecto.
  - Útil para validar que los datos ADK se pueden interpretar correctamente antes de evaluar.

### Cuándo usar cada prueba

- Usa `test_models.py` cuando cambies la estructura de datos o la serialización.
- Usa `test_evaluation.py` cuando ajustes la lógica de comparación de trayectorias.
- Usa `test_io.py` cuando cambies el formato o la carga/guardado de JSON.
- Usa `test_integration.py` cuando alteres el flujo general de evaluación o la orquestación.
- Usa `test_memory.py` cuando trabajes con estado persistente del agente.
- Usa `test_adk_evaluation.py` cuando quieras validar métricas adicionales de ADK.

### Ejecutar todas las pruebas

Desde el entorno virtual del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

O bien, si el entorno ya está activado:

```powershell
pytest -q
```

### Ejecutar pruebas individuales

```powershell
pytest -q tests/test_memory.py
pytest -q tests/test_adk_evaluation.py
pytest -q tests/test_integration.py
```

### Añadir nuevas pruebas

1. Crea un archivo nuevo `tests/test_<componente>.py`.
2. Importa el componente desde `adk_evaluator`.
3. Prefiere pruebas unitarias para lógica aislada y contratos de datos.
4. Usa pruebas de integración para el flujo completo de carga, evaluación y guardado.

## Cómo ampliar

Para agregar soporte real de Google ADK, incorpora un adaptador en `src/adk_evaluator/adapters/` y crea fixtures de datos en `tests/fixtures/`.
