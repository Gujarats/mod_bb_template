import contextlib
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch
from uuid import uuid4
import zipfile

from build_mod import ModBuilder


class ModBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_root = Path(__file__).parent / ".test-temp"
        self.temporary_root.mkdir(exist_ok=True)

    def make_temporary_project(self) -> Path:
        project = self.temporary_root / uuid4().hex
        project.mkdir()
        self.addCleanup(shutil.rmtree, project)
        return project

    def make_project(self, root: Path, game_data_dir: Path | None = None) -> Path:
        config = {
            "mod_id": "mod_example",
            "mod_name": "Example Mod",
            "version": "0.1.0",
            "game_data_dir": str(game_data_dir) if game_data_dir else "",
            "steam_app_id": "365360",
        }
        (root / "mod_config.json").write_text(json.dumps(config), encoding="utf-8")
        scripts = root / "scripts" / "!mods_preload"
        scripts.mkdir(parents=True)
        (scripts / "mod_example_loader.nut").write_text("// loader", encoding="utf-8")
        return root / "mod_config.json"

    def test_missing_brush_sources_are_skipped_and_scripts_are_packaged(self):
        root = self.make_temporary_project()
        config_path = self.make_project(root)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            archive = ModBuilder(config_path).build()

        self.assertIn("No unpacked brushes found; skipping brush build.", output.getvalue())
        self.assertTrue(archive.exists())
        with zipfile.ZipFile(archive) as package:
            self.assertIn("scripts/!mods_preload/mod_example_loader.nut", package.namelist())

    def test_brush_source_folders_are_packaged_as_brush_archives(self):
        root = self.make_temporary_project()
        config_path = self.make_project(root)
        brush_source = root / "unpacked_brushes" / "example_effect"
        brush_source.mkdir(parents=True)
        (brush_source / "metadata.xml").write_text("<brush />", encoding="utf-8")

        archive = ModBuilder(config_path).build()

        with zipfile.ZipFile(archive) as package:
            self.assertIn("brushes/example_effect.brush", package.namelist())
            with package.open("brushes/example_effect.brush") as brush_file:
                with zipfile.ZipFile(io.BytesIO(brush_file.read())) as brush:
                    self.assertIn("metadata.xml", brush.namelist())

    def test_launches_steam_only_after_successful_deployment(self):
        root = self.make_temporary_project()
        game_data_dir = root / "game-data"
        game_data_dir.mkdir()
        config_path = self.make_project(root, game_data_dir)

        with patch("build_mod.webbrowser.open") as open_steam:
            archive = ModBuilder(config_path, launch_game=True).build()

        self.assertTrue(archive.exists())
        self.assertTrue((game_data_dir / archive.name).exists())
        open_steam.assert_called_once_with("steam://run/365360")

    def test_disabled_launch_does_not_open_steam(self):
        root = self.make_temporary_project()
        config_path = self.make_project(root)

        with patch("build_mod.webbrowser.open") as open_steam:
            ModBuilder(config_path).build()

        open_steam.assert_not_called()
