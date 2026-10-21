# Glosario bilingüe de Odyssey-7

[Índice en español](README.md) · [English documentation](../../README.md)

Los identificadores del código, opciones de terminal y etiquetas de la interfaz
permanecen en inglés. Usa esta tabla para relacionarlos con las explicaciones.

| Término en inglés | Equivalente o explicación en español | Uso en el laboratorio |
| --- | --- | --- |
| Base model / Base LLM | Modelo base, sin el adaptador de este experimento | En Base tampoco recibe extractos de manuales; puede tener entrenamiento previo del proveedor |
| Inference | Inferencia: generar una salida con los pesos actuales | Responder una pregunta no es entrenar |
| Prompt | Mensajes e instrucciones que recibe el modelo | Los dos modos RAG usan mensajes idénticos en la comparación MLX |
| Context | Contexto disponible al generar | Incluye los fragmentos recuperados en RAG |
| Corpus | Colección de documentos | Tres manuales ficticios en Markdown |
| Chunk | Fragmento de documento | Una sección `##` con su título y cuerpo |
| Metadata | Metadatos | Archivo, sección, línea, ID, hash y URL del fragmento |
| Embedding | Representación vectorial de un texto | Permite comparar pregunta y secciones por similitud |
| Retriever | Recuperador | Selecciona fragmentos para el modelo |
| Vector store / index | Almacén o índice vectorial | FAISS mantiene los vectores en RAM en esta demostración |
| Cosine similarity | Similitud coseno | Puntaje de semejanza; no es confianza en la respuesta |
| Threshold | Umbral | Puntaje mínimo para aceptar una coincidencia |
| Top-k | Hasta las k coincidencias mejor ordenadas | El proyecto usa hasta tres, sujetas al umbral |
| RAG | Generación aumentada por recuperación | Añade documentos al contexto sin cambiar pesos |
| TF-IDF | Representación léxica basada en frecuencia de términos | Referencia que compara palabras y pares de palabras |
| Citation | Cita o referencia a una fuente | `[1]` remite a una fuente de esa respuesta, no a un archivo global |
| Traceability | Trazabilidad | Poder volver de la respuesta al extracto y documento cargado |
| Grounding | Sustento de la respuesta en evidencia | Hay que revisar afirmaciones, no solo etiquetas de cita |
| Hallucination | Alucinación: contenido inventado o no respaldado | Valores o procedimientos ausentes en los manuales |
| Abstention | Abstención | Reconocer que falta evidencia; puede decidirla la aplicación o el modelo |
| Fine-tuning | Ajuste fino | Entrenamiento adicional para una tarea o comportamiento |
| LoRA | Adaptación de bajo rango | Entrena parámetros adicionales pequeños y mantiene congelada la base |
| QLoRA | LoRA sobre una base cuantizada | La base de este experimento está a 4 bits |
| Adapter | Adaptador | Pesos adicionales que se cargan junto al modelo base compatible |
| Rank | Rango | Tamaño de la adaptación de bajo rango; aquí es 4 |
| Quantization | Cuantización | Representar pesos con menor precisión numérica |
| Token | Unidad de texto que procesa el modelo | No equivale necesariamente a una palabra |
| Batch size | Tamaño del lote | Número de ejemplos por lote; aquí es 1 |
| Learning rate | Tasa de aprendizaje | Magnitud que controla las actualizaciones; aquí es 0.0001 |
| Seed | Semilla | Inicializa operaciones aleatorias; no garantiza identidad entre entornos |
| Frozen weights | Pesos congelados | Parámetros de la base que no se actualizan en el entrenamiento LoRA |
| Prompt masking | Enmascaramiento del prompt | La pérdida se calcula sobre la respuesta del asistente |
| Loss | Pérdida | Objetivo numérico del entrenamiento; no es exactitud de respuestas |
| Train / validation / evaluation | Entrenamiento / validación / evaluación | 24 ejemplos sintéticos, 8 sintéticos separados y 10 preguntas sobre manuales |
| Data leakage | Fuga de datos | Usar información de evaluación para entrenar o seleccionar cambios y luego tratarla como independiente |
| Preflight | Comprobaciones previas | Validan configuración, datos, Metal, tokenización y generación antes de entrenar |
| Smoke test | Prueba mínima de funcionamiento | Un paso de entrenamiento y recarga del adaptador |
| Checkpoint | Punto de control | Momento en que se evalúa o guarda el entrenamiento |
| Recall@k | Cobertura de secciones esperadas entre las k recuperadas | No mide si la respuesta generada es correcta |
| Greedy sampling | Selección voraz | Elegir el siguiente token más probable; se usa en la comparación MLX |
| SHA256 / hash | Huella del contenido | Detecta diferencias de versión; no certifica veracidad |
| Backend | Motor o servicio que ejecuta la tarea | Ollama o el proceso local MLX para inferencia |
| Local-first | Prioridad al procesamiento local | Los documentos y la inferencia del ejemplo permanecen en el equipo |

Para una primera lectura, sigue este orden: **documento → fragmento → embedding →
recuperación → contexto → respuesta → verificación de fuentes**. Después estudia
**ejemplos sintéticos → validación previa → LoRA → comparación con la misma base**.
