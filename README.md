# GBA Background Generator (Tile Quantizer)

Desktop tool to convert regular images into **Game Boy Advance 4bpp background assets**:
- palette banks (up to 16 banks, 16 colors each),
- deduplicated/reduced 8x8 tile data,
- GBA text background tilemap data.

The app provides live previews (original, reconstructed map, tileset, palette) and exports files ready to integrate in a GBA project.

## Features

- PySide6 desktop UI for a full load -> process -> export workflow.
- Tile-based quantization options: palette bank count (1..16), dithering on/off, tile-grid padding.
- Tile optimization options: exact deduplication, horizontal/vertical flip deduplication, optional lossy reduction to fit a max tile budget.
- Multiple export targets: preview PNG, tileset PNG, tilemap CSV, palette binary (`.pal.bin`), tiles binary (`.tiles.bin`), map binary (`.map.bin`), optional C header metadata.

## Installation

Requirements:
- Python 3.10+ (recommended)
- `PySide6`
- `Pillow`

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install PySide6 Pillow
```

On PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Run

From repository root:

```bash
python src/main.py
```

## How to Use

1. Click **Load Image...** and pick a source image.
2. Adjust settings in the **Configuration** panel (quantization, tile reduction, and export options/output name).
3. Click **Process** to run the pipeline.
4. Inspect the quantized/reconstructed map preview, tileset preview, and palette banks.
5. Click **Export...** and choose an output folder.

If an error occurs, detailed debug info is appended to `debug.log`.

## Exported Files

Given `output_name = level1`, exports can include:

- `level1_preview.png`: reconstructed map preview.
- `level1_tileset.png`: rendered tileset preview.
- `level1_tilemap.csv`: tilemap entries as `tileIndex:paletteBank:hFlip:vFlip`.
- `level1.pal.bin`: GBA 15-bit little-endian palette data (banks padded to 16 colors).
- `level1.tiles.bin`: 4bpp tile data (32 bytes per 8x8 tile).
- `level1.map.bin`: GBA text background map entries (16-bit LE: tile index, flip flags, palette bank).
- `level1.h` (optional): basic metadata macros.

## Pipeline Summary

1. Load image (Pillow, converted to RGB).
2. Preprocess (optional padding to 8x8 grid).
3. Quantize into palette-banked indexed tiles.
4. Deduplicate tiles (exact + optional flip matching).
5. Reduce tile count if above max tile budget.
6. Render previews and build export artifacts.

## Project Structure

```text
src/
  app/        # Application bootstrap + controller
  gui/        # Main window, widgets, background worker
  services/   # Processing pipeline and export/encoding logic
  domain/     # Core models (Tile, TileMap, Palette, etc.)
  config/     # Quantization/reduction/export configuration models
  utils/      # Debug logging
```

## Current Scope

- Focused on **GBA text-background style 4bpp assets**.
- UI currently uses `median_cut` quantization method.
- No standalone CLI yet (GUI-first workflow).
