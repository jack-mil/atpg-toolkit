import unittest


class TestModule(unittest.TestCase):
    def test_version(self):
        """Test package version matches __version__ attribute."""
        from importlib import metadata

        import atpg_toolkit

        prop_ver = atpg_toolkit.__version__
        module_ver = metadata.version('atpg_toolkit')

        self.assertEqual(prop_ver, module_ver)
