# Odyssey-7: aprende ingeniería de IA en español

**Idioma / Language:** Español · [English](../../README.md)

Odyssey-7 es un laboratorio educativo que funciona con modelos locales. Su objetivo
es aprender mediante tutoriales paso a paso, experimentos reproducibles y una demo
local usable. Su cabina espacial permite comparar un modelo sin documentos, un
sistema RAG y un modelo
con un adaptador de formato más RAG. El objetivo es entender cada decisión,
inspeccionar las fuentes y reproducir los experimentos, incluidos sus errores.

![Cabina con una respuesta local y sus fuentes](../screenshots/cockpit-desktop.png)

## Ruta de aprendizaje

| Documento en español | Qué aprenderás | Versión en inglés |
| --- | --- | --- |
| [Tutorial de RAG](TUTORIAL.md) | Fragmentos, embeddings, búsqueda vectorial y trazabilidad | [Tutorial](../TUTORIAL.md) |
| [Ajuste con LoRA y MLX](FINETUNING.md) | Datos separados, validación previa y entrenamiento pequeño | [Fine-tuning](../FINETUNING.md) |
| [Evaluación](EVALUACION.md) | Métricas, comparación de tres modos y límites de los resultados | [Evaluation](../../evaluation/README.md) |
| [Demostración guiada](DEMO.md) | Recorrido para explicar el proyecto en tres minutos | [Demo](../DEMO.md) |
| [Glosario bilingüe](GLOSARIO.md) | Relación entre los términos en inglés y español | — |
| [Estado del proyecto](ROADMAP.md) | Fases completadas y trabajo opcional | [Roadmap](../ROADMAP.md) |
| [Validación en el navegador](VALIDACION_NAVEGADOR.md) | Comprobaciones observadas y capturas reales | [Browser validation](../BROWSER_VALIDATION.md) |

La documentación está disponible en ambos idiomas. La interfaz, los manuales
ficticios, los datos de entrenamiento y las preguntas de evaluación siguen en
**inglés**. Esta sección explica el mismo proyecto en español; no incorpora un
modelo nuevo ni demuestra que el sistema responda correctamente en español.
Los comandos, nombres de archivos, etiquetas de la interfaz y frases usadas por
las métricas se conservan literalmente para que puedas reproducir lo medido.

## Inicio rápido: Apple Silicon y Python 3.13

Instala Python 3.13, [uv](https://docs.astral.sh/uv/) y
[Ollama](https://ollama.com/). Ejecuta los comandos desde la raíz del repositorio:

```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.lock.txt
ollama pull qwen3:4b
ollama pull qwen3-embedding:4b
# Solo si Ollama no está ejecutándose, en otra terminal:
# ollama serve
uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000. La primera consulta RAG carga el modelo de embeddings
y construye en memoria un índice con seis secciones. No necesitas una clave de API
en la nube ni un servicio externo de base de datos vectorial. La descarga del
modelo de embeddings ocupa aproximadamente 2.5 GB, además del modelo de chat.

Si el puerto está ocupado, usa `uvicorn app.main:app --port 8001` y abre ese puerto.
Detén el servidor con Ctrl+C. Reinícialo después de modificar los manuales o los
modelos. Los modelos deben descargarse antes de usarlos: la aplicación no los
descarga automáticamente ni cambia de servicio si falla el configurado.

## Comprueba el entorno y reproduce la evaluación

Con `.venv` activado:

```bash
uv pip check
python -m pytest -q
python -m scripts.evaluate --backend tfidf --output runs/tfidf.json
python -m scripts.evaluate --output runs/vector.json
# Compara las mismas diez preguntas en Base y RAG; no entrena el modelo:
python -m scripts.evaluate --generate --output runs/base-rag.json
```

En el Mac de desarrollo, un M5 Pro con 48 GB de RAM y Python 3.13.15, se registraron
32 pruebas aprobadas y un aviso de obsolescencia de Starlette/httpx. Es evidencia
de ese entorno, no una garantía de que cualquier instalación funcionará sin cambios.

Para el tercer modo, sigue primero la [guía de MLX y LoRA](FINETUNING.md). Necesita
un entorno opcional separado, un modelo pequeño de Qwen3 y un adaptador validado.
Después podrás ejecutar:

```bash
CHAT_BACKEND=mlx .venv/bin/uvicorn app.main:app --reload
```

Los tres modos usarán entonces el mismo modelo MLX de 0.6B parámetros. No confundas
esa comparación con la demostración predeterminada de Ollama, que usa Qwen3 4B.

## Configuración disponible

Define estas variables antes de iniciar el servidor:

| Variable | Valor predeterminado | Función |
| --- | --- | --- |
| `OLLAMA_URL` | `http://localhost:11434` | Servicio local de inferencia y embeddings |
| `OLLAMA_MODEL` | `qwen3:4b` | Modelo de chat de Ollama |
| `EMBEDDING_MODEL` | `qwen3-embedding:4b` | Modelo que convierte textos en vectores |
| `RAG_RETRIEVER` | `vector` | Usa `tfidf` para la referencia léxica |
| `RAG_MIN_SCORE` | `0.55` | Umbral de similitud coseno para la búsqueda vectorial |
| `CHAT_BACKEND` | `ollama` | Usa `mlx` para comparar los tres modos con la misma base |

La similitud no es una probabilidad de que la respuesta sea correcta. Un fragmento
puede tratar del mismo tema sin contener la respuesta. Del mismo modo, un formato
correcto y una cita existente no garantizan que los hechos estén respaldados.

**Solo simulación educativa:** los procedimientos de la nave son ficticios y no
sirven como instrucciones de seguridad reales.
