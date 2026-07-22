#!/usr/bin/env python3
"""Build, optionally deploy, and optionally launch a Battle Brothers mod."""

from __future__ import annotations

import argparse
import platform
import json
import shutil
import subprocess
import webbrowser
import zipfile
import time
from pathlib import Path

from build_brushes import BrushBuilder


class ModBuilder:
    """Package a template mod using only Python's standard library."""

    CONTENT_DIRECTORIES = ("scripts", "gfx", "ui", "brushes")
    DEFAULT_CONFIG = {
        "mod_id": "mod_template",
        "mod_name": "Battle Brothers Mod Template",
        "version": "0.1.0",
        "game_data_dir": "",
        "steam_app_id": "365360",
    }

    def __init__(
        self,
        config_path: Path | str,
        game_data_dir: Path | str | None = None,
        launch_game: bool = False,
        restart_game: bool = False,
    ) -> None:
        self.config_path = Path(config_path).resolve()
        self.project_dir = self.config_path.parent
        self.config = self._load_config()
        configured_data_dir = self.config.get("game_data_dir", "")
        self.game_data_dir = Path(game_data_dir or configured_data_dir) if (game_data_dir or configured_data_dir) else None
        self.launch_game = launch_game
        self.should_restart_game = restart_game

    def _load_config(self) -> dict[str, str]:
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(
                json.dumps(self.DEFAULT_CONFIG, indent=2) + "\n",
                encoding="utf-8",
            )
            print(
                f"Warning: mod_config.json was not found. "
                f"Created default config at: {self.config_path}"
            )
            print(
                "Please edit this file before releasing your mod so mod_id, "
                "mod_name, and version match your project."
            )

        with self.config_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
        required = ("mod_id", "mod_name", "version", "steam_app_id")
        missing = [key for key in required if not config.get(key)]
        if missing:
            raise ValueError(f"Missing required configuration values: {', '.join(missing)}")
        return config

    def build_brushes(self) -> None:
        BrushBuilder(self.project_dir).build()

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

    def is_game_running(self) -> bool:
        """Return whether Battle Brothers is currently running on Windows."""
        if platform.system() != "Windows":
            return False

        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq BattleBrothers.exe", "/NH"],
            capture_output=True,
            text=True,
            check=True,
        )
        return "battlebrothers.exe" in result.stdout.lower()

    def _restart_game(self) -> None:
        """Request a running Battle Brothers process to exit before launch."""
        if platform.system() != "Windows":
            return

        if not self.is_game_running():
            return

        print("Warning: restarting Battle Brothers can discard unsaved game progress.")
        subprocess.run(["taskkill", "/IM", "BattleBrothers.exe"], check=True)
        for _ in range(8):
            time.sleep(0.25)
            if not self.is_game_running():
                return

        subprocess.run(["taskkill", "/F", "/IM", "BattleBrothers.exe"], check=True)
        if self.is_game_running():
            raise RuntimeError("Battle Brothers is still running after force termination.")

    def _launch_game(self) -> None:
        if self.should_restart_game:
            self._restart_game()
        webbrowser.open(f"steam://run/{self.config['steam_app_id']}")

    def build(self) -> Path:
        print(f"Building {self.config['mod_name']} {self.config['version']}")
        self.build_brushes()
        archive = self.create_archive()
        deployed_archive = self.deploy(archive)
        if self.launch_game and deployed_archive is not None:
            self._launch_game()
        elif self.launch_game:
            print("Game launch skipped because the mod was not deployed.")
        else:
            print("Game launch not requested; skipping.")
        return archive


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Battle Brothers mod template.")
    parser.add_argument("--config", default="mod_config.json", help="Path to the JSON configuration file.")
    parser.add_argument("--game-data-dir", help="Override the game data directory in the configuration.")
    parser.add_argument("--launch-game", action="store_true", help="Launch Battle Brothers through Steam after deployment.")
    parser.add_argument(
        "-r",
        "--restart-game",
        action="store_true",
        help="Restart Battle Brothers before launch.",
    )
    arguments = parser.parse_args()
    builder = ModBuilder(
        arguments.config,
        arguments.game_data_dir,
        arguments.launch_game or arguments.restart_game,
        arguments.restart_game,
    )
    builder.build()


if __name__ == "__main__":
    main()
