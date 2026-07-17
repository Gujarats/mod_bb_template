#!/usr/bin/env python3
"""Compile Battle Brothers brush sources into binary ``.brush`` assets."""

from __future__ import annotations

from pathlib import Path

from buildscript.python.bbrusher import BBrusher


class BrushBuilder:
    """Build every immediate brush source folder in a mod project."""

    def __init__(self, project_dir: Path | str) -> None:
        self.project_dir = Path(project_dir).resolve()
        self.source_root = self.project_dir / "unpacked_brushes"
        self.output_root = self.project_dir / "brushes"
        self.gfx_root = self.project_dir / "gfx"
        self.bbrusher = BBrusher()

    def build(self) -> list[Path]:
        """Compile non-empty brush sources and return their binary output paths."""
        if not self.source_root.exists():
            print("No unpacked brushes found; skipping brush build.")
            return []

        source_folders = sorted(path for path in self.source_root.iterdir() if path.is_dir())
        if not source_folders:
            print("No unpacked brushes found; skipping brush build.")
            return []

        self.output_root.mkdir(exist_ok=True)
        self.gfx_root.mkdir(exist_ok=True)
        built_brushes = []
        for source_folder in source_folders:
            metadata = source_folder / "metadata.xml"
            if not metadata.exists():
                print(f"Skipping brush without metadata.xml: {source_folder.name}")
                continue

            output_brush = self.output_root / f"{source_folder.name}.brush"
            self.bbrusher.pack_brush_from_dir_smart(
                output_brush,
                source_folder,
                self.gfx_root,
            )
            built_brushes.append(output_brush)
            print(f"Built brush: {output_brush.name}")
        return built_brushes
