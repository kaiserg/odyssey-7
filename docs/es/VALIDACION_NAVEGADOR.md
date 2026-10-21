# Qué se comprobó en el navegador

**Idioma / Language:** Español · [English](../BROWSER_VALIDATION.md) · [Índice en español](README.md)

El 20 de octubre de 2026 se realizaron comprobaciones nativas en Google Chrome en
el Mac M5 Pro de 48 GB. Este documento explica esa evidencia existente: no es una
nueva ejecución, una suite automática entre navegadores ni una auditoría formal
de accesibilidad.

## Comprobaciones observadas

| Función | Resultado observado |
| --- | --- |
| Archivo de manuales | Tres documentos y seis secciones enlazadas; conteos desde la API |
| Preguntas de ejemplo | Rellenan y enfocan el campo sin enviar |
| Tecla Enter | Envía una pregunta real y vuelve al estado de disponibilidad |
| Base | Responde sin fuentes documentales y muestra ese estado explícitamente |
| RAG | Muestra las fuentes devueltas para la respuesta |
| Fine-tuned + RAG | Genera con el adaptador MLX local validado |
| Pregunta sobre el capitán | Abstención canónica con cero fuentes en modo de recuperación |
| Expansión de fuentes | Extracto original, similitud y enlace al archivo y línea |
| Enlace documental | Nueva pestaña con archivo, línea, SHA256 del documento y texto |
| Historial de evidencia | Una respuesta anterior restaura sus fuentes después de otra consulta |
| Vista móvil | Envío real a 390 × 844 píxeles CSS |
| Vista de escritorio | Revisión de la ventana de escritorio y de 1440 × 900; corrección del solapamiento de instrumentos y pie |
| Adaptador sin configurar | El tercer modo queda deshabilitado en configuración solo Ollama |
| Falla de embeddings o chat | Error visible, sin evidencia adjunta y controles disponibles de nuevo |

Las fallas se probaron con un servidor temporal separado, usando deliberadamente
`OLLAMA_URL=http://127.0.0.1:9` y `CHAT_BACKEND=ollama`. La pestaña y ese servidor
se cerraron al terminar; se mantuvo el servidor de trabajo. No se cambiaron pesos,
adaptadores, prompts ni configuración de entrenamiento para esas pruebas visuales.

## Capturas reales compartidas

- [Escritorio](../screenshots/cockpit-desktop.png): ventana de 1440 × 900 píxeles CSS,
  capturada con proporción de píxeles 2, como PNG de 2880 × 1800. Muestra una
  respuesta real de Fine-tuned + RAG y la primera fuente expandida. El archivo
  y la conversación tienen desplazamiento independiente.
- [Móvil](../screenshots/cockpit-mobile.png): ventana de 390 × 844 píxeles CSS,
  capturada con proporción 2, como PNG de 780 × 1688. El chat aparece primero;
  el archivo y los instrumentos siguen debajo.

Las capturas se tomaron con **Capture screenshot** de Chrome DevTools, sin pestañas
personales ni controles del navegador. No son maquetas ni respuestas inventadas.
Para reproducir la vista, inicia la aplicación MLX validada, selecciona Fine-tuned +
RAG y pregunta `What do I do when oxygen pressure drops?`. En escritorio, expande
la primera sección. Una captura muestra un ejemplo de salida, no exactitud general.

La dirección visual usa el concepto local `Odyssey-7_AI_Cockpit_Console.png` como
referencia de composición, marcos y detalles ámbar. La implementación usa CSS y un
SVG original; no incorpora el mapa de bits del concepto como fondo de la página.
Las ilustraciones están identificadas como simulación y los indicadores describen
configuración, no telemetría real ni salud comprobada de los servicios.

## Qué no se ha certificado

La interfaz incorpora etiquetas accesibles, estados `aria-pressed`, región de chat
anunciable, enlace para saltar al campo y estilos de foco. Se comprobaron Enter y
la recuperación del foco. No se auditaron lectores de pantalla, conformidad de
contraste, todas las dimensiones, dispositivos físicos ni Safari/Firefox. Las
ventanas muy bajas pueden necesitar desplazamiento de página. El historial reside
en memoria y se pierde al recargar.

Esta sección bilingüe no cambia la interfaz ni repite las pruebas: traduce su
explicación y mantiene las mismas capturas y evidencias.
