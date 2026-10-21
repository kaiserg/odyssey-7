# Cómo evaluar recuperación, respuestas y formato

**Idioma / Language:** Español · [English](../../evaluation/README.md) · [Índice en español](README.md)

## 1. Conserva las mismas preguntas

[questions.jsonl](../../evaluation/questions.jsonl) contiene diez preguntas en inglés:
seis con respuesta en los manuales, una por sección, y cuatro sin respuesta.
Cada registro incluye un identificador, las secciones esperadas y términos que
se buscan en la respuesta. Es un conjunto pequeño para enseñar el proceso, no una
muestra representativa del rendimiento general. No debe usarse para entrenar.

Esta documentación explica los resultados existentes en español. No traduce el
conjunto de evaluación ni valida el comportamiento del modelo en otro idioma.
Traducir las preguntas produciría otro experimento que habría que medir por separado.

Desde la raíz, con `.venv` activado:

```bash
python -m scripts.evaluate --backend tfidf --output runs/tfidf.json
python -m scripts.evaluate --output runs/vector.json
python -m scripts.evaluate --generate --output runs/base-rag.json
```

La evaluación vectorial necesita Ollama y `qwen3-embedding:4b`. La generación
predeterminada usa además `qwen3:4b`. Estas órdenes no entrenan ningún modelo.
Los informes JSON conservan respuestas originales, secciones recuperadas, puntajes,
umbral, modelos, fecha, entorno y hashes del corpus y del conjunto de preguntas.

## 2. Distingue las métricas

| Nombre usado en el proyecto | Qué mide | Qué no demuestra |
| --- | --- | --- |
| `recall_at_3` | Fracción de secciones esperadas entre hasta tres coincidencias; promedio sobre las seis preguntas respaldadas | Que el modelo use bien el texto recuperado |
| Abstención de recuperación | Fracción de las cuatro preguntas no respaldadas que quedan sin coincidencias | Que el modelo haya aprendido a abstenerse |
| `abstained` | Presencia de la frase literal `Not found in the provided manual.` | Todas las formas de expresar incertidumbre |
| `expected_term_coverage` | Coincidencia de subcadenas esperadas, sin distinguir mayúsculas | Corrección semántica o veracidad de toda la respuesta |
| `cites_expected_section` | Al menos una etiqueta numérica apunta a una sección esperada | Que cada afirmación esté respaldada por esa cita |
| `invalid_citation_count` | Etiquetas numéricas fuera del rango de fuentes entregadas | Toda cita inventada, especialmente si no tiene forma numérica |
| `format_compliant` | Dos líneas con `Answer:` y `Sources:` según el patrón del evaluador | Calidad o integridad del contenido |

Por ejemplo, una respuesta puede citar `[1]` correctamente y mezclar un dato de
otra sección. También puede decir «no tengo esa información» sin usar la frase
canónica: la revisión humana reconoce la incertidumbre, pero esa métrica no.

## 3. Revisa primero la recuperación

Resultados guardados en el M5 Pro de 48 GB, el 20 de octubre de 2026:

| Recuperador | Recall@3: seis preguntas respaldadas | Sin coincidencias: cuatro no respaldadas |
| --- | --- | --- |
| TF-IDF | 1.0 | 1/4, equivalente a 0.25 |
| Embeddings Qwen + FAISS, umbral 0.55 | 1.0 | 3/4, equivalente a 0.75 |

Fuentes: [informe TF-IDF](../../evaluation/tfidf-retrieval.json) e
[informe vectorial](../../evaluation/vector-retrieval.json).

La búsqueda vectorial todavía recupera la sección de revisión rutinaria al preguntar
por la frecuencia de reemplazo del depurador. El tema coincide, pero el documento
no especifica el intervalo. Es el ejemplo central de por qué similitud y capacidad
de responder no son lo mismo. El umbral es inicial; no se afirma que esté calibrado
con un conjunto independiente.

## 4. Mantén separado el experimento de Ollama

[base-rag.json](../../evaluation/base-rag.json) contiene veinte resultados locales
con Qwen3 4B: las diez preguntas en Base y en RAG, temperatura 0.2 y semilla 7.
En esa ejecución histórica, RAG cubrió todos los términos esperados y citó una
sección esperada en las seis preguntas respaldadas. Las cuatro preguntas no
respaldadas recibieron la abstención canónica.

Base obtuvo aproximadamente 0.067 en cobertura de términos y no aportó fuentes.
Su métrica de abstención literal fue 0.0, aunque la revisión manual encontró
incertidumbre sobre capitán, contraseña, intervalo del depurador y combustible.
También inventó valores y procedimientos en otras respuestas. Las salidas guardadas
son artefactos del modelo para inspeccionar, no material de consulta confiable.

## 5. Compara los tres modos MLX

Después de preparar y validar el adaptador mediante la [guía de LoRA](FINETUNING.md):

```bash
CHAT_BACKEND=mlx .venv/bin/python -m scripts.evaluate --generate --include-finetuned --output runs/mlx-three-way.json
```

[mlx-three-way.json](../../evaluation/mlx-three-way.json) usa la misma base Qwen3
0.6B de 4 bits en todos los modos. Los dos modos RAG reciben mensajes idénticos;
solo Fine-tuned + RAG carga el adaptador de rango 4 entrenado durante 40 pasos.
Los tres reciben la instrucción de formato, usan selección voraz, semilla 7 y
un límite de 256 tokens. El modelo y las instrucciones difieren del experimento
histórico de Ollama: no atribuyas esas diferencias al adaptador.

| Métrica registrada | Base | RAG | Fine-tuned + RAG |
| --- | --- | --- | --- |
| Formato estricto, seis preguntas respaldadas | 0/6 | 1/6 | 5/6 |
| Cobertura media de términos esperados | 0.000 | 0.500 | 0.533 |
| Cita una sección esperada, seis preguntas | 0/6 | 6/6 | 6/6 |
| Abstención canónica, cuatro preguntas no respaldadas | 0/4 | 4/4 | 4/4 |
| Etiquetas numéricas de cita fuera de rango | 2 | 0 | 0 |

## 6. Lee los errores además de la tabla

- Ambos modos RAG dieron **19.0 kPa** como presión nominal, aunque la revisión
  rutinaria especifica **21.0 kPa**. Citar una sección esperada no evitó el error.
- El adaptador conservó la prohibición de reiniciar durante el acoplamiento,
  pero **omitió la secuencia de reinicio** que sí había dado RAG sin adaptar.
- La respuesta adaptada sobre rutas indicó correctamente dos confirmaciones;
  RAG sin adaptar solo nombró el archivo fuente para esa pregunta.
- Ambos contestaron correctamente «15 percent» en la pregunta de potencia, pero
  la comprobación esperaba «fifteen» y puntuó cero. La métrica se conservó sin
  reajustarla después de observar las respuestas.
- Base expresó incertidumbre con otras palabras. Su 0/4 no significa que nunca
  reconociera desconocimiento.
- En tres preguntas no respaldadas, la aplicación se abstuvo antes de generar.
  No son evidencia de aprendizaje del adaptador. La del depurador sí llegó a
  ambos modelos y ambos se abstuvieron.

La pérdida sintética de validación bajó de 3.020 a 0.001, según el registro de
entrenamiento. Las plantillas de entrenamiento y validación son muy parecidas;
resolver esa tarea sencilla no prueba una mejora general de preguntas y respuestas.
No se seleccionó otro entrenamiento usando estas respuestas de evaluación.

El resultado defendible es una **mejora estrecha del formato**, con errores y pérdidas
de contenido todavía presentes. Para conclusiones más amplias hacen falta preguntas
independientes, métricas semánticas mejor definidas y revisión de afirmaciones frente
a las fuentes. Este cambio de documentación no ejecuta ni modifica las mediciones.
