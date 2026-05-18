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

Para una evaluación más completa, prueba el dataset extendido:

```powershell
.\.venv\Scripts\adk-evaluator --ground-truth data/sample_ground_truth_complex.json --predictions data/sample_predictions_complex.json --output results_complex.json
```

## Estructura

- `src/adk_evaluator/`: código fuente principal
- `tests/`: pruebas unitarias
- `data/`: ejemplos de datos de ground truth y predicciones
- `docs/`: guía de arquitectura y pruebas

## Desarrollo

Ejecuta las pruebas:

```powershell
pytest
```

### Tipos de pruebas disponibles

- `tests/test_models.py`: pruebas unitarias de los modelos de dominio (`Trajectory`, `TrajectoryPoint`, `GroundTruth`, `Prediction`).
- `tests/test_evaluation.py`: pruebas unitarias de la lógica de evaluación de trayectorias y métricas.
- `tests/test_io.py`: pruebas unitarias de carga y guardado de datos JSON.
- `tests/test_integration.py`: prueba de integración del flujo completo desde carga de datos hasta generación de resultados.
- `tests/test_memory.py`: pruebas unitarias del componente de memoria del agente, cómo guarda, recupera y protege el estado de ejecución.

### Ejecutar todas las pruebas

Desde el entorno virtual del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

O bien, si el entorno ya está activado:

```powershell
pytest -q
```

## Cómo ampliar

Para agregar soporte real de Google ADK, incorpora un adaptador en `src/adk_evaluator/adapters/` y crea fixtures de datos en `tests/fixtures/`.
