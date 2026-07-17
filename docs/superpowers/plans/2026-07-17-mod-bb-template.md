# Battle Brothers Mod Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a reusable Battle Brothers mod repository with optional brush packaging, ZIP deployment, and optional Steam launch.

**Architecture:** A committed JSON configuration supplies mod identity and optional game data directory. A standard-library Python builder discovers present content folders, optionally turns each folder in `unpacked_brushes/` into a `.brush` archive, creates the mod ZIP, deploys it, and optionally opens Steam.

**Tech Stack:** Python 3 standard library, Squirrel, Modern Hooks, MSU.

## Global Constraints

- Missing `unpacked_brushes/` is a normal condition: print a skip message and continue.
- Never delete source `scripts/`, `gfx/`, `ui/`, or brush source files.
- ZIP contents include only existing mod-content folders.
- Steam launch is opt-in through `--launch-game` and happens only after deployment succeeds.

---

### Task 1: Create template structure and configuration

**Files:**
- Create: `.gitignore`, `LICENSE`, `README.md`, `AGENT.md`, `mod_config.json`
- Create: `scripts/!mods_preload/mod_template_loader.nut`
- Create: `gfx/.gitkeep`, `ui/.gitkeep`, `unpacked_brushes/.gitkeep`

- [ ] **Step 1:** Define `mod_config.json` with `mod_id`, `mod_name`, `version`, `game_data_dir`, and `steam_app_id`.
- [ ] **Step 2:** Add a minimal Modern Hooks loader whose mod identity values are clear placeholders.
- [ ] **Step 3:** Document copying the template, changing configuration and loader identity, adding Squirrel/assets, and building.
- [ ] **Step 4:** Verify the committed tree contains no Aura Routing-specific code or names.

### Task 2: Build and deploy without mandatory brushes

**Files:**
- Create: `build_mod.py`, `tests/test_build_mod.py`

**Interfaces:**
- Produces: `ModBuilder(config_path, game_data_dir=None, launch_game=False)`.
- Produces: `ModBuilder.build() -> Path`.

- [ ] **Step 1:** Write tests proving missing `unpacked_brushes/` prints `No unpacked brushes found; skipping brush build.` and still creates a ZIP containing `scripts/`.
- [ ] **Step 2:** Implement JSON configuration loading, readable configuration output, and directory discovery for `scripts`, `gfx`, `ui`, and generated `brushes`.
- [ ] **Step 3:** Implement brush creation by ZIP-compressing each immediate folder under `unpacked_brushes/` into `brushes/<folder>.brush`; skip absent/empty source folders.
- [ ] **Step 4:** Implement ZIP creation in `dist/`, then copy it to the configured game data directory when supplied.
- [ ] **Step 5:** Run `python -m unittest discover -s tests -v` and require all tests to pass.

### Task 3: Add optional Steam launch and finish documentation

**Files:**
- Modify: `build_mod.py`, `tests/test_build_mod.py`, `README.md`

- [ ] **Step 1:** Write tests showing `--launch-game` invokes `webbrowser.open("steam://run/<steam_app_id>")` only after deployment.
- [ ] **Step 2:** Add the `--launch-game` flag and launch method; print a skip message when omitted.
- [ ] **Step 3:** Document `python build_mod.py`, `python build_mod.py --game-data-dir "..." `, and `python build_mod.py --launch-game`.
- [ ] **Step 4:** Run the full test suite and inspect the archive listing from a temporary test build.

