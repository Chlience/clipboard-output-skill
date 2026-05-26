import argparse
import ctypes
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "copy_text.py"

spec = importlib.util.spec_from_file_location("copy_text", SCRIPT_PATH)
copy_text = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(copy_text)


class DummyFunc:
    def __init__(self):
        self.argtypes = None
        self.restype = None


class DummyUser32:
    def __init__(self):
        self.OpenClipboard = DummyFunc()
        self.EmptyClipboard = DummyFunc()
        self.SetClipboardData = DummyFunc()
        self.CloseClipboard = DummyFunc()


class DummyKernel32:
    def __init__(self):
        self.GlobalAlloc = DummyFunc()
        self.GlobalLock = DummyFunc()
        self.GlobalUnlock = DummyFunc()
        self.GlobalFree = DummyFunc()


class CopyTextTests(unittest.TestCase):
    def test_read_text_rejects_missing_source(self):
        args = argparse.Namespace(file=None, text=None, stdin=False, encoding="utf-8")

        with mock.patch.object(sys, "stdin", io.StringIO("unexpected")):
            with self.assertRaises(copy_text.ClipboardError) as raised:
                copy_text.read_text(args)

        self.assertIn("--file, --text, or --stdin", str(raised.exception))

    def test_read_text_allows_explicit_stdin(self):
        args = argparse.Namespace(file=None, text=None, stdin=True, encoding="utf-8")

        with mock.patch.object(sys, "stdin", io.StringIO("from stdin")):
            self.assertEqual(copy_text.read_text(args), "from stdin")

    def test_sensitive_text_requires_explicit_override(self):
        with self.assertRaises(copy_text.ClipboardError):
            copy_text.validate_text("OPENAI_API_KEY=sk-proj-example", allow_sensitive=False)

        copy_text.validate_text("OPENAI_API_KEY=sk-proj-example", allow_sensitive=True)

    def test_non_sensitive_text_is_allowed(self):
        copy_text.validate_text("Write a Windows batch file that starts WeChat twice.", allow_sensitive=False)

    def test_windows_clipboard_api_uses_pointer_sized_types(self):
        user32 = DummyUser32()
        kernel32 = DummyKernel32()

        copy_text.configure_windows_clipboard_api(user32, kernel32)

        self.assertEqual(kernel32.GlobalAlloc.restype, ctypes.c_void_p)
        self.assertEqual(kernel32.GlobalLock.restype, ctypes.c_void_p)
        self.assertEqual(user32.SetClipboardData.argtypes, [ctypes.c_uint, ctypes.c_void_p])
        self.assertEqual(user32.OpenClipboard.argtypes, [ctypes.c_void_p])


if __name__ == "__main__":
    unittest.main()
