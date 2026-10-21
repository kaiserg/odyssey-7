# Cockpit browser validation

Validated on the M5 Pro / 48 GB development Mac in Google Chrome, October 20, 2026.
These are observed manual/native browser checks, not an automated cross-browser
suite or a formal accessibility audit. The existing local MLX app served the live
checks at port 8000. No evaluation report was regenerated for this frontend change.

## Observed checks

| Check | Observed result |
| --- | --- |
| Archive load | Three manuals, six linked sections; counts populated from the API |
| Example selection | Fills the composer and focuses it without sending |
| Enter to transmit | Sends a real local question and returns to ready state |
| RAG response | Shows the returned source list and a response mode label |
| Fine-tuned response | Generates with the validated local MLX adapter |
| Base response | Generates without document sources; empty evidence state is explicit |
| Unsupported captain question | Retrieval mode returns canonical abstention with zero sources |
| Expand evidence | Shows the original excerpt, similarity and document/line link |
| Source link | Opens the file name, original line, full-document SHA256 and excerpt in a separate tab |
| Evidence history | An earlier response restores its original source list after a later question |
| Mobile submission | A real fine-tuned question completes at a 390 × 844 CSS viewport |
| Desktop layout | Inspected at native 1864 × 1123 page space and responsive 1440 × 900; fixed instrument-stack/footer overlap in the shorter view |
| Missing adapter configuration | Fine-tuned control stays disabled in an Ollama-only configuration |
| Embedding service failure | Visible error, no attached evidence, controls usable again |
| Chat service failure | Visible error, no attached evidence, controls usable again |
| Chrome console | No application console messages observed during the successful screenshot session |

The outage checks used a separate temporary server with `OLLAMA_URL=http://127.0.0.1:9`
and `CHAT_BACKEND=ollama`, intentionally making both services unreachable. Its tab
and server were closed afterward. The user's working server was left running.
No model weights, adapters, prompts or training settings changed in this phase.

## Real screenshots

- [Desktop](screenshots/cockpit-desktop.png): 1440 × 900 CSS viewport, captured at
  device pixel ratio 2 (2880 × 1800 PNG). A real Fine-tuned + RAG oxygen response
  is shown with its first source expanded. The archive and chat scroll independently.
- [Mobile](screenshots/cockpit-mobile.png): 390 × 844 CSS viewport, captured at
  device pixel ratio 2 (780 × 1688 PNG). The chat is first, with the composer at the
  bottom of the console; the archive and instrument panels follow below the fold.

Both files were captured through Chrome DevTools' **Capture screenshot** command.
They contain the live page only, with no browser chrome, personal tabs or fabricated
answers. They are examples of model output, not evidence of general answer accuracy.
To reproduce, start the validated MLX app, select Fine-tuned + RAG and ask
`What do I do when oxygen pressure drops?`. Expand the first retrieved section.
Use Chrome's responsive toolbar with the dimensions above and capture the viewport.

## Visual and interaction scope

The layout follows the local `Odyssey-7_AI_Cockpit_Console.png` concept: a central
chat display, orbital viewport, framed panels, amber trim and a vessel schematic.
The implementation uses CSS and an original SVG; the concept bitmap is not shipped
as a page background. Decorative scenery is labeled as illustration/simulation.
Archive counts and model labels come from the API. Similarity is explicitly not a
confidence score; configuration is explicitly not service-health telemetry.

The UI includes semantic landmarks, mode `aria-pressed` state, a labeled input,
visible focus styles, a chat live region, a skip link and reduced-motion support.
Enter submission and input focus restoration were exercised. Screen-reader behavior,
color-contrast conformance, physical mobile devices, Safari/Firefox and every possible
viewport were not audited. Very short windows can require page scrolling. Chat and
evidence history are in memory and reset on reload.
