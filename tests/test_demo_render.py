import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "demo" / "render_demo.py"


class DemoRenderTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location("render_demo", SCRIPT_PATH)
        module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(module)
        return module

    def test_filter_contains_demo_message(self):
        module = self.load_module()

        filter_graph = module.build_filter_graph()

        self.assertIn("TUI output to clipboard", filter_graph)
        self.assertIn("Original Codex-style output", filter_graph)
        self.assertIn("$ codex", filter_graph)
        self.assertIn("Ctrl+C", filter_graph)
        self.assertIn("direct paste result", filter_graph)
        self.assertIn("·   #!/usr/bin/env bash", filter_graph)
        self.assertIn("gutter dots + padding", filter_graph)
        self.assertIn("npm run build", filter_graph)
        self.assertIn("enable='between(t,0.7,3.6)'", filter_graph)
        self.assertIn("enable='gte(t,7.2)'", filter_graph)
        self.assertNotIn("Windows", filter_graph)
        self.assertNotIn("╭─ build.sh", filter_graph)
        self.assertNotIn("Weixin.exe", filter_graph)
        self.assertNotIn("Clipboard Output Skill", filter_graph)
        self.assertNotIn("Skill paste", filter_graph)
        self.assertNotIn("clipboard-output-skill", filter_graph)

    def test_default_output_path(self):
        module = self.load_module()

        self.assertEqual(module.DEFAULT_OUTPUT.name, "clipboard-output-demo.gif")
        self.assertEqual(module.DEFAULT_OUTPUT.parent.name, "demo")

    def test_ffmpeg_command_uses_palette_pipeline(self):
        module = self.load_module()

        command = module.build_ffmpeg_command(module.DEFAULT_OUTPUT)
        joined = " ".join(command)

        self.assertIn("palettegen", joined)
        self.assertIn("paletteuse", joined)
        self.assertEqual(command[-1], str(module.DEFAULT_OUTPUT))


if __name__ == "__main__":
    unittest.main()
