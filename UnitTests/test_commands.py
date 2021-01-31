import unittest
# cpsc-351-wmccarthy.slack.com
# https://app.slack.com/workspace-signin?redir=%2Fgantry%2Fclient

class TestCommands(unittest.TestCase):
    def test_VERSION(self):
        self.assertTrue(isinstance(VERSION, packaging.version.Version))

    def test_STATE_PATH(self):
        self.assertTrue(isinstance(STATE_PATH, pathlib.Path))
        self.assertEqual('.json', STATE_PATH.suffix)

    def test_DEFAULT_BUILD_CONFIG(self):
        self.assertTrue(isinstance(DEFAULT_BUILD_CONFIG, BuildConfig))
        self.assertEqual(VERSION, DEFAULT_BUILD_CONFIG.version)
        self.assertEqual(STATE_PATH, DEFAULT_BUILD_CONFIG.state_path)
