#!/usr/bin/env python3
"""Compile Battle Brothers brush sources into binary ``.brush`` assets."""

from __future__ import annotations

import json
from pathlib import Path

from buildscript.python.bbrusher import BBrusher


class BrushBuilder:
    """Build every immediate brush source folder in a mod project."""

    def __init__(self, project_dir: Path | str) -> None:
        self.project_dir = Path(project_dir).resolve()
        self.source_root = self.project_dir / "unpacked_brushes"
        self.output_root = self.project_dir / "brushes"
        self.gfx_root = self.project_dir / "gfx"
        self.manifest_path = self.project_dir / ".brush_build_manifest.json"
        self.bbrusher = BBrusher()

    def clean_previous_outputs(self) -> None:
        """Remove only brush and atlas files created by the previous build."""
        if not self.manifest_path.exists():
            return
        generated_files = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        allowed_roots = (self.output_root.resolve(), self.gfx_root.resolve())
        for relative_path in generated_files:
            generated_file = (self.project_dir / relative_path).resolve()
            if any(generated_file.is_relative_to(root) for root in allowed_roots) and generated_file.is_file():
                generated_file.unlink()
        self.manifest_path.unlink()

    def write_manifest(self, generated_files: list[Path]) -> None:
        relative_paths = sorted(
            file_path.relative_to(self.project_dir).as_posix() for file_path in generated_files
        )
        self.manifest_path.write_text(json.dumps(relative_paths, indent=2) + "\n", encoding="utf-8")

    def build(self) -> list[Path]:
        """Compile non-empty brush sources and return their binary output paths."""
        self.clean_previous_outputs()
        if not self.source_root.exists():
            print("No unpacked brushes found; skipping brush build.")
            self.write_manifest([])
            return []

        source_folders = sorted(path for path in self.source_root.iterdir() if path.is_dir())
        if not source_folders:
            print("No unpacked brushes found; skipping brush build.")
            self.write_manifest([])
            return []

        self.output_root.mkdir(exist_ok=True)
        self.gfx_root.mkdir(exist_ok=True)
        built_brushes = []
        generated_files = []
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
            generated_files.extend(self.output_root.glob(f"{source_folder.name}*.brush"))
            generated_files.extend(self.gfx_root.glob(f"{source_folder.name}*.png"))
            print(f"Built brush: {output_brush.name}")
        self.write_manifest(generated_files)
        return built_brushes
