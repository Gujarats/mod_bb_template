# Battle Brothers Mod Template

Starter repository for a Battle Brothers mod using Modern Hooks, MSU, and a Python build/deploy script.

# Special Thanks to
 - [Legends Mod](https://github.com/Battle-Brothers-Legends/Legends-public)

# Prerequisites
```
1. Python 3
2. Install the brush compiler dependency: `pip install Pillow`
```

## Create a mod

1. Copy this folder and rename it for your mod.
2. Update `mod_config.json` with the new ID, name, version, and optionally `game_data_dir`.
3. Update `scripts/!mods_preload/mod_template_loader.nut` to use the same ID, name, and version.
4. Add Squirrel files under `scripts/`, assets under `gfx/` or `ui/`, and unpacked brushes under `unpacked_brushes/`.

Modern Hooks and MSU (version 1.9.0 or newer) are required by the starter loader; adjust its requirements if your mod differs.

## Build

```powershell
python -m pip install -e .
modbb --help

python build_mod.py
python build_mod.py --game-data-dir "C:\Program Files (x86)\Steam\steamapps\common\Battle Brothers\data"
python build_mod.py --launch-game
python build_mod.py --game-data-dir "C:\Program Files (x86)\Steam\steamapps\common\Battle Brothers\data" --restart-game
python build_mod.py -r --game-data-dir "C:\Program Files (x86)\Steam\steamapps\common\Battle Brothers\data"
```

You can also use the global CLI command after `pip install -e .`:

```powershell
modbb --config "E:\path\to\your\mod_bb_template\mod_config.json" --restart-game --game-data-dir "C:\Program Files (x86)\Steam\steamapps\common\Battle Brothers\data"
```

If `modbb` is not recognized, it usually means the Scripts folder is not on PATH:

```powershell
& "C:\Users\gujar\AppData\Local\Python\pythoncore-3.14-64\Scripts\modbb.exe" --help
```

Add it for the current PowerShell session:

```powershell
$env:Path += ";C:\Users\gujar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
```

Persist it for future sessions:

```powershell
$current = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable(
  "Path",
  "$current;C:\Users\gujar\AppData\Local\Python\pythoncore-3.14-64\Scripts",
  "User"
)
```

Then open a new terminal and run:

```powershell
modbb --help
```

The builder writes `dist/<mod_id>.zip`. It packages any existing `scripts/`, `gfx/`, `ui/`, and generated `brushes/` directories. Each immediate folder inside `unpacked_brushes/` must contain `metadata.xml` and its source PNG files. The bundled Battle Brothers brush compiler creates a binary `brushes/<folder>.brush` plus `gfx/<folder>.png`; both are added to the ZIP. A game launch occurs only when deployment succeeds.

Do not edit `buildscript/python/bbrusher/`. It implements the Battle Brothers `.brush` binary format, texture-atlas packing, UV coordinates, and sprite metadata serialization.

## .brush file
 - the script will produce gfx/some_image_name.png
 - brush/some_file.brush
 - if above file are not being generated, it could be wrong in the path script or the script has some bugs.
