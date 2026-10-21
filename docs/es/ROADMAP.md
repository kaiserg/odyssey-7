# Estado y ruta de aprendizaje del proyecto

**Idioma / Language:** Español · [English](../ROADMAP.md) · [Índice en español](README.md)

Las cuatro fases previstas de la demostración están completadas según la evidencia
registrada en el repositorio. «Completada» significa que existe la demostración
pequeña y validada descrita; no implica calidad de producción, cobertura de todos
los navegadores ni exactitud general del modelo.

| Fase | Trabajo completado | Qué puedes estudiar |
| --- | --- | --- |
| 1. Cabina inicial | Interfaz adaptable, manuales ficticios, FastAPI, Ollama, Base/RAG y referencia TF-IDF; comprobaciones HTTP y posteriores pruebas en Chrome | [Inicio rápido](README.md) y [recorrido](DEMO.md) |
| 2. RAG semántico | Embeddings locales, FAISS, fragmentos por sección, metadatos, enlaces a fuentes y evaluación de recuperación | [Tutorial RAG](TUTORIAL.md) y [evaluación](EVALUACION.md) |
| 3. LoRA con MLX | Revisión fija del modelo, entorno separado, datos sintéticos, comprobaciones previas, prueba de un paso, entrenamiento de 40 pasos y comparación de tres modos | [Guía LoRA](FINETUNING.md) |
| 4. Presentación del portafolio | Cabina refinada, esquema SVG original, historial de fuentes por respuesta, diagramas, capturas reales y guion de demostración | [Demostración](DEMO.md) y [validación visual](VALIDACION_NAVEGADOR.md) |

La documentación en español añade una ruta de estudio paralela a la inglesa.
No modifica el código, la interfaz, los manuales ni los datos de entrenamiento o
evaluación. Tampoco añade mediciones de respuestas en español.

## Evidencia registrada

- Entorno de desarrollo: Apple M5 Pro con 48 GB de RAM y Python 3.13.15.
- Suite sin inferencia real: 32 pruebas aprobadas, con un aviso de Starlette/httpx.
- Recuperación vectorial: recall@3 de 1.0 en seis preguntas respaldadas y ausencia
  de coincidencias en tres de cuatro preguntas no respaldadas.
- Entrenamiento: 24 ejemplos sintéticos y 8 de validación; rango 4 en cuatro capas,
  40 actualizaciones y aproximadamente 0.360 millones de parámetros entrenables.
- Comparación MLX: formato estricto de 1/6 con RAG a 5/6 con adaptador; ambos
  conservan errores de hechos y el adaptado omite pasos de navegación.
- Navegador: comprobaciones nativas en Chrome y capturas de escritorio y móvil.

Los [informes originales](EVALUACION.md) y el [roadmap en inglés](../ROADMAP.md)
conservan el detalle histórico y los identificadores de los primeros commits.

## Límites y trabajo opcional

Quedan fuera de lo validado Safari, Firefox, dispositivos móviles físicos y una
auditoría formal de accesibilidad. También sería necesario un conjunto independiente
más amplio y revisión semántica de hechos para sostener conclusiones de exactitud.
Las métricas actuales no verifican cada afirmación frente a su cita.

Si se quisiera medir el sistema en español, haría falta diseñar y ejecutar una
evaluación específica sin confundirla con la traducción de estas guías. No se ha
hecho en esta fase. El alcance sigue siendo una demostración educativa pequeña:
sin corpus grande, plataforma empresarial ni entrenamientos costosos adicionales.
