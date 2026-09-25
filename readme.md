# DAFNE: a dataset of Fresco fragments

## Intro

DAFNE generates datasets of fragments from input images. Supported image formats: `png`, `jpg`, `jpeg`.

## Project layout

- `DAFNE/core/` — implementation modules (package name: `core`).
- `DAFNE/scripts/` — thin shell wrappers to run the CLIs (`.sh` files).
- `DAFNE/requirements.txt` — lists the external Python packages required to run the `core` modules.

## Setup (virtual environment)

Follow the platform section that matches your environment.

Unix (macOS / Linux):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r DAFNE/requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r DAFNE/requirements.txt
```

Windows (cmd.exe):

```cmd
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r DAFNE/requirements.txt
```

## How it works

DAFNE simulates the real-world deterioration and shattering of frescos and paintings to generate synthetic puzzle-reassembly benchmark datasets. The core algorithm follows these steps:

1. **Seed Generation & Voronoi Tessellation**: Candidate points are sampled across the image using a Poisson-disk-like constraint. The image is then partitioned into Voronoi cells based on these seeds to extract initial fragments.
2. **Stochastic Merging**: Adjacent Voronoi cells are randomly merged to create realistic, jagged, and non-convex fragment shapes.
3. **Morphological Degradation**: Fragments undergo morphological erosion (using rotated rectangular kernels) and edge smoothing to simulate physical chipping and wear.
4. **Color Degradation**: HSV color values are randomly perturbed to simulate pigment fading and atmospheric weathering.
5. **2D Transformation & Ground Truth Tracking**: Each fragment is randomly rotated. Precise bounding-box offsets and angles are saved as ground truth for reassembly.
6. **Defect Injection**: A percentage of fragments can be intentionally discarded (to simulate missing pieces), and spurious distractor fragments from other datasets can be injected.

### Example

| Original Image | Reconstructed Output |
| :---: | :---: |
| <img src="docs/original.png" width="400"> | <img src="docs/ricostructed_image.png" width="400"> |
| *Original source fresco* | *Synthetic fragmentation with erosion and missing pieces* |

## Output structure

For each processed image, DAFNE generates a timestamped output directory containing:

- `fragments/`: Individual isolated fragment images (e.g., `fragment_000.png`) in RGBA format with transparent backgrounds.
- `resources/`:
  - `fragment_info.txt`: Ground truth coordinates, bounding box offsets, and rotation angles for every fragment.
  - `fragmentation_info.txt`: The exact hyperparameter values used for the generation run.
  - `spurious_info.txt`: *(Optional)* Count and filenames of injected distractor pieces.
- `ricostructed_image.png`: A reassembled visual overlay showing the ground-truth alignment and erosion gaps.

## Running

Unix (macOS / Linux): make the shell scripts executable and run them:

```bash
chmod +x DAFNE/scripts/*.sh
./DAFNE/scripts/dafne_run.sh <input_directory> --output_directory <out_dir> --file_path <params.txt>

# Removal CLI:
./DAFNE/scripts/remove_fragments_run.sh <input_directory> <original_image> --output_directory <out_dir> --file_path <params.txt>
```

Windows:

```powershell
# Either run the Python module directly (recommended on Windows):
python -m core.DAFNE <input_directory> --output_directory <out_dir> --file_path <params.txt>

# Or, if you have Git Bash / WSL, run the shell scripts from that environment:
bash ./DAFNE/scripts/dafne_run.sh <input_directory> --output_directory <out_dir> --file_path <params.txt>
```

Use `-h` to show the underlying `argparse` help:

```bash
# Unix
./DAFNE/scripts/dafne_run.sh -h

# Windows (module form)
python -m core.DAFNE -h
```

## Parameters file format

Example `params.txt`:

```
seed: 3500
num_fragments: 400
min_distance: 10
erosion_probability: 0.65
erosion_percentage: 25
removal_percentage: 10
num_spurious: 4
```

`removal_percentage` and `num_spurious` are optional.
