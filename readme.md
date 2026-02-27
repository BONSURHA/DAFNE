# DAFNE: a dataset of Fresco fragments

## Intro

DAFNE generates datasets of fragments from input images. Supported image formats: `png`, `jpg`, `jpeg`.

## Project layout (important)

- `DAFNE/core/` — implementation modules (package name: `core`).
- `DAFNE/scripts/` — thin shell wrappers to run the CLIs (`.sh` files).
- `DAFNE/requirements.txt` — lists the external Python packages required to run the `core` modules.
  Install them with `pip install -r DAFNE/requirements.txt` (see below).

## Setup (virtual environment)

Follow the platform section that matches your environment.

Unix (macOS / Linux):

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

2. Install minimal runtime packages:

```bash
python -m pip install numpy opencv-python Pillow
```

Windows (PowerShell):

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force  # if needed to run scripts
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Windows (cmd.exe):

```cmd
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
```

Notes:

- `DAFNE/requirements.txt` contains the external packages required by `core` (run the command below to install them):

```bash
python -m pip install -r DAFNE/requirements.txt
```

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
num_spurius: 4
```

`removal_percentage` and `num_spurius` are optional.

## Notes & blockers

- Native extensions or GPU-specific packages found in some subprojects are not packaged here — they require system toolchains (CUDA, compilers) and are intentionally left untouched.
- If you want a single installable package, I can create a `pyproject.toml`/`setup.cfg` and a proper `pip`-installable layout. Tell me if you'd like that.
