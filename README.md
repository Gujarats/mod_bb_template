# Battle Brothers Mod Template

Starter repository for a Battle Brothers mod using Modern Hooks, MSU, and a Python build/deploy script.

## Create a mod

1. Copy this folder and rename it for your mod.
2. Update `mod_config.json` with the new ID, name, version, and optionally `game_data_dir`.
3. Update `scripts/!mods_preload/mod_template_loader.nut` to use the same ID, name, and version.
4. Add Squirrel files under `scripts/`, assets under `gfx/` or `ui/`, and unpacked brushes under `unpacked_brushes/`.

Modern Hooks and MSU (version 1.9.0 or newer) are required by the starter loader; adjust its requirements if your mod differs.

## Build

```powershell
python build_mod.py
python build_mod.py --game-data-dir "C:\Program Files (x86)\Steam\steamapps\common\Battle Brothers\data"
python build_mod.py --launch-game
```

The builder writes `dist/<mod_id>.zip`. It packages any existing `scripts/`, `gfx/`, `ui/`, and generated `brushes/` directories. Each immediate folder inside `unpacked_brushes/` becomes `brushes/<folder>.brush`. A game launch occurs only when deployment succeeds.
