# Arquitectura del proyecto ADK Evaluator

## Capas

- `models`: define los objetos de dominio (`GroundTruth`, `Trajectory`, `Prediction`, `EvaluationResult`).
- `evaluation`: implementa la lógica de comparación de trayectorias y métricas, incluido un emparejamiento más robusto de predicción contra ground truth.
- `io`: abstrae la carga y el guardado de datos de entrada/salida.
- `service`: orquesta la evaluación entre múltiples trayectorias y predicciones.
- `cli`: expone un punto de entrada sencillo para ejecutar evaluaciones desde la línea de comandos.

## Principios de diseño

- Single Responsibility Principle: cada módulo gestiona una preocupación única.
- Open/Closed Principle: se pueden agregar nuevos evaluadores sin modificar los existentes.
- Data classes: el modelo usa `dataclass` para claridad y serialización simple.

## Cómo escalar

1. Añadir nuevos tipos de evaluadores en `evaluation.py`.
2. Crear adaptadores específicos de ADK en `src/adk_evaluator/adapters/`.
3. Separar métricas complejas en un paquete `metrics/` si surge la necesidad.
4. Mantener los datos de prueba en `tests/fixtures/` y la configuración en `pyproject.toml`.
