# Cómo agregar pruebas

## Buenas prácticas

- Usa datos de ejemplo pequeños y representativos.
- Cubre casos normales y casos límite, por ejemplo trayectorias vacías y predicciones con distinta longitud.
- Evita dependencias externas en las pruebas unitarias.

## Estructura recomendada

- `tests/test_models.py`: valida la creación y serialización de modelos.
- `tests/test_evaluation.py`: comprueba los cálculos de métricas.
- `tests/test_io.py`: verifica la carga y el guardado de JSON.
- `tests/test_memory.py`: valida el comportamiento de la memoria del agente, cómo guarda el estado y cómo crea snapshots inmutables.

## Ejecución

```powershell
pytest
```

## Añadir nuevos tests

1. Crea un archivo nuevo `tests/test_<componente>.py`.
2. Importa el componente desde `adk_evaluator`.
3. Usar `tmp_path` para archivos temporales cuando trabajes con IO.
