"""
Some tests that will ensure tests are being run with installed package, not from the cwd.
Ensures that the package is properly installed and importable, and version metadeta matches code.
"""

import unittest

import atpg_toolkit


class TestPackage(unittest.TestCase):
    def test_version(self):
        """Test package version matches __version__ attribute."""
        from importlib import metadata

        prop_ver = atpg_toolkit.__version__
        module_ver = metadata.version('atpg_toolkit')

        self.assertEqual(prop_ver, module_ver)
