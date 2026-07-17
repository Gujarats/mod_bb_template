#!/usr/bin/env python3
"""Build, optionally deploy, and optionally launch a Battle Brothers mod."""

from __future__ import annotations

import argparse
import json
import shutil
import webbrowser
import zipfile
from pathlib import Path


class ModBuilder:
    """Package a template mod using only Python's standard library."""

    CONTENT_DIRECTORIES = ("scripts", "gfx", "ui", "brushes")

    def __init__(self, config_path: Path | str, game_data_dir: Path | str | None = None,
                 launch_game: bool = False) -> None:
        self.config_path = Path(config_path).resolve()
        self.project_dir = self.config_path.parent
        self.config = self._load_config()
        configured_data_dir = self.config.get("game_data_dir", "")
        self.game_data_dir = Path(game_data_dir or configured_data_dir) if (game_data_dir or configured_data_dir) else None
        self.launch_game = launch_game

    def _load_config(self) -> dict[str, str]:
        with self.config_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
        required = ("mod_id", "mod_name", "version", "steam_app_id")
        missing = [key for key in required if not config.get(key)]
        if missing:
            raise ValueError(f"Missing required configuration values: {', '.join(missing)}")
        return config

    def build_brushes(self) -> None:
        source_root = self.project_dir / "unpacked_brushes"
        source_folders = [path for path in source_root.iterdir() if path.is_dir()] if source_root.exists() else []
        if not source_folders:
            print("No unpacked brushes found; skipping brush build.")
            return

        output_root = self.project_dir / "brushes"
        output_root.mkdir(exist_ok=True)
        for source_folder in source_folders:
            files = [path for path in source_folder.rglob("*") if path.is_file()]
            if not files:
                continue
            output_file = output_root / f"{source_folder.name}.brush"
            with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as brush:
                for file_path in files:
                    brush.write(file_path, file_path.relative_to(source_folder).as_posix())
            print(f"Built brush: {output_file.name}")

    def create_archive(self) -> Path:
        dist_dir = self.project_dir / "dist"
        dist_dir.mkdir(exist_ok=True)
        archive = dist_dir / f"{self.config['mod_id']}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
            for directory_name in self.CONTENT_DIRECTORIES:
                directory = self.project_dir / directory_name
                if not directory.exists():
                    continue
                for file_path in directory.rglob("*"):
                    if file_path.is_file() and file_path.name != ".gitkeep":
                        package.write(file_path, file_path.relative_to(self.project_dir).as_posix())
        return archive

    def deploy(self, archive: Path) -> Path | None:
        if self.game_data_dir is None:
            print("No game data directory configured; skipping deployment.")
            return None
        self.game_data_dir.mkdir(parents=True, exist_ok=True)
        destination = self.game_data_dir / archive.name
        shutil.copy2(archive, destination)
        print(f"Deployed {archive.name} to {self.game_data_dir}")
        return destination

    def build(self) -> Path:
        print(f"Building {self.config['mod_name']} {self.config['version']}")
        self.build_brushes()
        archive = self.create_archive()
        deployed_archive = self.deploy(archive)
        if self.launch_game and deployed_archive is not None:
            webbrowser.open(f"steam://run/{self.config['steam_app_id']}")
        elif self.launch_game:
            print("Game launch skipped because the mod was not deployed.")
        else:
            print("Game launch not requested; skipping.")
        print(f"Created {archive}")
        return archive


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Battle Brothers mod template.")
    parser.add_argument("--config", default="mod_config.json", help="Path to the JSON configuration file.")
    parser.add_argument("--game-data-dir", help="Override the game data directory in the configuration.")
    parser.add_argument("--launch-game", action="store_true", help="Launch Battle Brothers through Steam after deployment.")
    arguments = parser.parse_args()
    ModBuilder(arguments.config, arguments.game_data_dir, arguments.launch_game).build()


if __name__ == "__main__":
    main()
