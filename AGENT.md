# Template conventions

- Keep the mod identity in `mod_config.json` and the preload loader consistent.
- Put generated archives in `dist/`; do not commit them.
- `unpacked_brushes/` is source content, while `brushes/` is generated build output.
- `buildscript/python/bbrusher/` is vendored Battle Brothers brush-format code. Do not modify it.
