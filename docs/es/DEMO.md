# Demostración guiada en tres minutos

**Idioma / Language:** Español · [English](../DEMO.md) · [Índice en español](README.md)

## Prepara la demostración

Para Base y RAG con Ollama, sigue el [inicio rápido](README.md#inicio-rápido-apple-silicon-y-python-313).
Para los tres modos, reproduce primero la [preparación y validación del adaptador](FINETUNING.md).
Después, con Ollama activo para los embeddings:

```bash
CHAT_BACKEND=mlx .venv/bin/uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000. El panel muestra configuración, no disponibilidad
comprobada del servicio. Con MLX, los tres modos usan la misma base de 0.6B.
Un clon del repositorio sin pesos y adaptador locales no habilita el tercer modo.
La interfaz y las preguntas reproducibles siguen en inglés; tú puedes explicar
el recorrido en español.

## Sigue el recorrido

1. **Sin documentos.** Selecciona Base y pregunta
   `What do I do when oxygen pressure drops?`. Explica: «El modelo no tiene el
   manual. Puede reconocer incertidumbre o inventar acciones». El panel de fuentes
   debe quedar vacío.
2. **Con recuperación.** Selecciona RAG y repite la misma pregunta. Expande la
   sección de oxígeno y abre su enlace. Muestra archivo, línea y hash. Explica:
   «Ahora podemos comparar cada afirmación con el texto que recibió el modelo».
3. **Con adaptación.** Selecciona Fine-tuned + RAG y repite. Busca las líneas
   `Answer:` y `Sources:`. Usa **Inspect evidence** en respuestas anteriores para
   recuperar sus fuentes. Explica: «Solo cambia el adaptador; los fragmentos y
   las instrucciones del experimento controlado son los mismos».
4. **Sin dato disponible.** Pregunta `Who is the captain?`. Explica: «Aquí no hay
   coincidencias suficientes; la aplicación devuelve una abstención sin generar.
   Esto es una regla del sistema, no una capacidad aprendida del adaptador».
5. **Con texto relacionado, pero insuficiente.** Pregunta
   `How often must the CO2 scrubber be replaced?`. Explica: «Una sección puede
   hablar del depurador sin indicar cuándo reemplazarlo. El modelo debe reconocer
   que falta el dato aunque reciba contexto».
6. **Con resultados y límites.** Abre la [comparación medida](EVALUACION.md).
   Explica: «El formato pasó de 1/6 a 5/6, pero ambos modos RAG fallaron la presión
   nominal y el adaptado perdió pasos de navegación. Un formato mejor no equivale
   a una respuesta más correcta».

## Explica las decisiones de ingeniería

- El corpus pequeño permite inspeccionar las seis secciones y sus fuentes.
- Ollama genera embeddings y FAISS realiza búsqueda exacta en memoria; no hay
  otro servicio de base de datos. TF-IDF permite comparar una referencia léxica.
- El adaptador usa 24 ejemplos sintéticos de formato, no hechos del manual ni
  las diez preguntas de evaluación. Hay otros ocho ejemplos de validación.
- El entorno MLX está separado del entorno de la aplicación.
- La validación previa y una prueba de un paso preceden al entrenamiento limitado.
- Los hashes, la revisión del modelo, las versiones y las respuestas originales
  permiten revisar lo que se midió. No garantizan salidas idénticas en todo entorno.

## Reproduce las comprobaciones

```bash
.venv/bin/python -m pytest -q
uv pip check --python .venv/bin/python
uv pip check --python .venv-mlx/bin/python
CHAT_BACKEND=mlx .venv/bin/python -m scripts.evaluate --generate --include-finetuned --output runs/mlx-three-way.json
```

Las capturas y comprobaciones visuales están en la
[validación del navegador](VALIDACION_NAVEGADOR.md). Las preguntas de este recorrido
no son una evaluación de comprensión en español. Todo procedimiento de la nave es
ficticio y no constituye una instrucción de seguridad real.
