# REVISION_PROFUNDA_NOTEBOOKS_V1

Marker: `FISICA_COMPUTACIONAL_DEEP_NOTEBOOK_REVIEW_V1`
Resource: `MCP_SCIKI_N8N_FISICA_COMPUTACIONAL_REVIEW_RESOURCE_V1`
Repo: `jbermejovega/Computacional`
Mode: read-only static notebook review. Notebook code is not executed.

## Activation

This document deploys the deep review resource for Fisica Computacional exams/workbooks as an invariant workflow:

- MCP resource active: true
- SCIKI map active: true
- N8N workflow exported: true
- GitHub Actions invariant workflow active: true
- Notebook-by-notebook review: true
- Replay-safe: true
- Contents read-only: true
- No notebook code execution during review: true

The canonical validator is `scripts/revision_fisica_computacional/notebook_deep_review.py` and the CI entrypoint is `.github/workflows/fisica-computacional-notebook-review.yml`.

## Notebook Inventory

| Path | Status | Cells | Markdown | Code | Review state |
| --- | --- | ---: | ---: | ---: | --- |
| `Obligatorio4.ipynb` | parsed | 11 | 6 | 5 | NEEDS_REVISION |
| `Voluntarios/Voluntario1/notebook.ipynb` | parsed | 18 | 11 | 7 | NEEDS_REVISION |
| `obligatorios/obligatorio1/sistemas_solar_notebook.ipynb` | parsed | 21 | 14 | 7 | NEEDS_REVISION |
| `obligatorios/obligatorio2/Informe _ising.ipynb` | empty file | 0 | 0 | 0 | BLOCKED |
| `obligatorios/obligatorio2/Obligatorio2_informe.ipynb` | parsed | 13 | 7 | 6 | NEEDS_REVISION |
| `obligatorios/obligatorio4/Obligatorio4.ipynb` | parsed | 11 | 6 | 5 | NEEDS_REVISION |

## Global Findings

### P0 - Empty notebook blocks review

`obligatorios/obligatorio2/Informe _ising.ipynb` is a zero-byte notebook. It cannot be opened, executed, rendered, or graded as a notebook artifact.

Required action:

- Delete it if it is an accidental duplicate, or replace it with a valid notebook.
- Keep `obligatorios/obligatorio2/Obligatorio2_informe.ipynb` as the canonical Ising report unless there is a separate intended report.

### P1 - Obligatorio 4 is duplicated at repository root and inside `obligatorios/obligatorio4`

Both `Obligatorio4.ipynb` and `obligatorios/obligatorio4/Obligatorio4.ipynb` describe the same three-body Moon transfer report and carry the same code structure.

Required action:

- Declare one canonical location.
- Prefer `obligatorios/obligatorio4/Obligatorio4.ipynb` because it matches the repository organization.
- Replace the root copy with a pointer, or remove it after confirming no external link depends on it.

### P1 - Reproducibility depends on generated files and shell/C++ execution

Several notebooks depend on `%%writefile`, `!g++`, `!./binary`, `.dat`, `.png`, `.gif`, or `.mp4` artifacts. This is valid for the course workflow, but it must be explicit and replayable.

Required action:

- Add a short "Reproducibility" cell to each notebook.
- State the order: write C++ source, compile, execute, generate data, then run Python visualization.
- Name expected generated files and whether they are tracked or regenerated.

### P1 - Long code cells mix report and engine

The review found long code cells in:

- `Obligatorio4.ipynb`, cell 10, about 149 lines of C++ RK4 engine.
- `obligatorios/obligatorio4/Obligatorio4.ipynb`, cell 10, about 149 lines of C++ RK4 engine.
- `Voluntarios/Voluntario1/notebook.ipynb`, cell 16, about 305 lines of C++ galaxy engine.
- `Voluntarios/Voluntario1/notebook.ipynb`, cells 9 and 15, long Python analysis/plot cells.
- `obligatorios/obligatorio1/sistemas_solar_notebook.ipynb`, cell 15, about 82 lines of Verlet integration loop.
- `obligatorios/obligatorio2/Obligatorio2_informe.ipynb`, cell 7, about 118 lines of animation code.

Required action:

- Move reusable engines into `.cpp` or `.py` files already present in the repo.
- Keep notebooks as orchestration, explanation, plots, and conclusions.
- Add a compact code cell that calls the script and checks expected outputs.

### P1 - Execution counts are inconsistent

Several notebooks contain unexecuted code cells or stale execution state. The review is static and does not execute notebooks, but it detects missing execution counts.

Required action:

- Run each canonical notebook from a clean kernel in order.
- Clear stale failed outputs.
- Commit either clean unexecuted notebooks plus deterministic generated artifacts, or fully executed notebooks with all outputs current. Do not mix states accidentally.

## Notebook-by-Notebook Review

### `Obligatorio4.ipynb`

Subject: restricted three-body Moon transfer, RK4 integration, conserved `H'`, animation and diagnostic plot.

Strengths:

- Clear report headings: introduction, trajectories, conservation proof, numerical conservation, annex.
- Uses C++ for the numerical engine and Python for visualization.
- No saved error outputs were found.

Risks:

- Duplicate of `obligatorios/obligatorio4/Obligatorio4.ipynb`.
- Long C++ cell embeds the whole RK4 engine in the notebook.
- Requires local shell execution: `!g++ -O3 cohete.cpp -o cohete` and `!./cohete`.
- Depends on generated `data.dat`, `cohete.gif`, and `constante_H.png`.
- Not all code cells have execution counts.

Actions:

- Make this file non-canonical or remove after preserving the organized copy.
- If it stays, add a first-cell notice pointing to the canonical notebook.

### `obligatorios/obligatorio4/Obligatorio4.ipynb`

Subject: same as root Obligatorio 4, likely the correct canonical location.

Strengths:

- Good scientific narrative around `H'` conservation.
- Keeps major physics stages visible to the reader.
- No saved error outputs were found.

Risks:

- Same long embedded C++ engine as the root copy.
- Shell execution and generated files are implicit rather than checked.
- All code execution counts are missing in the parsed notebook, suggesting a clean-but-unexecuted or copied state.

Actions:

- Keep this as canonical Obligatorio 4.
- Add an explicit generated-file contract: `cohete.cpp`, `cohete`, `data.dat`, `cohete.gif`, `constante_H.png`.
- Move RK4 code to `cohete.cpp` or verify notebook-written source exactly matches `obligatorios/obligatorio4/cohete.cpp`.

### `Voluntarios/Voluntario1/notebook.ipynb`

Subject: galaxy formation from solar-system particles, central black hole, gravitational interactions, mass flow, rotation curve, spatial distribution.

Strengths:

- Strong narrative structure with objectives, methodology, results, conclusions, bibliography/anexos.
- Rich output surface: density/inertia, mass flow, velocity map, rotation curve.
- No saved error outputs were found.

Risks:

- One empty code cell.
- Multiple long cells, including a 305-line C++ engine.
- Requires compilation/execution with `!g++ -O3 galaxia.cpp -o simular_galaxia` and `!./simular_galaxia`.
- Depends on generated data files: `datos_galaxia.dat`, `flujo_masa.dat`, `mapa_final.dat`, `curva_rotacion.dat`, and image outputs.
- Execution counts are missing, so current outputs are not proven replayed from a clean kernel.

Actions:

- Remove empty code cell.
- Move the C++ engine into `Voluntarios/Voluntario1/agujero_negro.cpp` or a clearly named `galaxia.cpp` tracked file.
- Add a resource-cost note because the generated `datos_galaxia.dat` is large.
- Add validation cells for conservation/qualitative plausibility: active particle count, absorbed mass, radial bins, and rotation-curve error bars.

### `obligatorios/obligatorio1/sistemas_solar_notebook.ipynb`

Subject: Solar System simulation with Verlet, energy and angular momentum conservation.

Strengths:

- Smallest and most modular notebook among the parsed required notebooks.
- Code is already split across several cells.
- All code cells have execution counts.
- No saved error outputs were found.

Risks:

- Markdown exists but lacks explicit `#`/`##` section headings, making notebook navigation and grading harder.
- The main Verlet loop cell is long and should be split.
- Depends on `condiciones_i.txt`, `planets_data.dat`, and `energia_momento.txt`.

Actions:

- Add headings: objective, equations, algorithm, implementation, validation, results, conclusion.
- Split the integration loop into force calculation, update step, diagnostics, and output write sections.
- Add a check that `energia_momento.txt` exists and that relative drift remains within an stated tolerance.

### `obligatorios/obligatorio2/Informe _ising.ipynb`

Subject: intended Ising report, but file is empty.

Strengths:

- None detectable because the file has zero bytes.

Risks:

- Blocks notebook rendering and review.
- Name overlaps with the valid `Obligatorio2_informe.ipynb` and may confuse graders.

Actions:

- Remove or replace this file.
- If it is meant to be canonical, restore it from notebook history.

### `obligatorios/obligatorio2/Obligatorio2_informe.ipynb`

Subject: 2D Ising model, Monte Carlo, Metropolis, animation, magnetization versus temperature and phase transition.

Strengths:

- Clear report headings and physics flow.
- Includes critical temperature marker around `T ~= 2.27`.
- No saved error outputs were found.

Risks:

- No code cell has execution count.
- Animation cell is long and mixes data parsing, frame preparation, rendering, saving, and display.
- Requires compilation/execution of two C++ programs: animation generation and magnetization sweep.
- Depends on `ising_data.dat`, `magnetizacion_data.dat`, MP4/PDF outputs, and generated C++ files.

Actions:

- Split animation code into loader, frame parser, animator, and save/display cells.
- Add seed, lattice size, iteration count, thermalization cut, and measurement window to a parameter table.
- Add finite-size caveat near the `T ~= 2.27` marker.
- Replace or delete the empty `Informe _ising.ipynb` so this report is unambiguous.

## Invariant Review Contract

The deployed workflow must preserve these invariants:

```yaml
FISICA_COMPUTACIONAL_DEEP_NOTEBOOK_REVIEW_V1:
  notebook_by_notebook: true
  mcp_resource_active: true
  sciki_map_active: true
  n8n_workflow_exported: true
  no_notebook_code_execution: true
  read_only_static_review: true
  generated_witness: build/revision_fisica_computacional/notebook-review-witness.json
  human_summary: build/revision_fisica_computacional/notebook-review-witness.md
  blocked_findings_are_reported_not_hidden: true
```

## Next Canonical Fix Set

1. Delete or restore `obligatorios/obligatorio2/Informe _ising.ipynb`.
2. Choose canonical Obligatorio 4 location and remove or redirect the duplicate root notebook.
3. Add reproducibility cells and generated-file contracts to every canonical notebook.
4. Move long C++/Python engines out of notebooks where a tracked source file already exists.
5. Run notebooks from clean kernels and commit a consistent output policy.
