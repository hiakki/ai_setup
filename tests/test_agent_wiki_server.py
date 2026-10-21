from pathlib import Path
import tempfile
import unittest

from agent_wiki_server import configure, configure_compose, env_values, validate_public_url


class AgentWikiServerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source = Path(self.temporary.name)

    def test_remote_server_requires_https_and_signup_allowlist(self):
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            validate_public_url('http://wiki.example.test')
        self.assertEqual(validate_public_url('https://wiki.example.test/'),
                         'https://wiki.example.test')
        with self.assertRaisesRegex(ValueError, 'allowed-emails'):
            configure(self.source, 'https://wiki.example.test', 8090, '')
        configure(self.source, 'https://wiki.example.test', 8090, '*@example.test')
        values = env_values(self.source / '.env')
        self.assertEqual(values['PUBLIC_BASE_URL'], 'https://wiki.example.test')
        self.assertEqual(values['ALLOWED_EMAILS'], '*@example.test')
        self.assertEqual(values['SECURE_COOKIES'], 'true')
        self.assertEqual(len(values['SECRET_KEY']), 64)
        self.assertNotEqual(values['SECRET_KEY'], 'change-me')
        override = configure_compose(self.source)
        content = override.read_text()
        self.assertIn('DEV_MODE: "false"', content)
        self.assertIn('127.0.0.1:${AGENT_WIKI_PORT:-8090}:80', content)
        self.assertIn('ports: !override', content)

    def test_existing_private_configuration_is_preserved(self):
        configure(self.source, 'http://localhost:8090', 8090, '')
        before = (self.source / '.env').read_bytes()
        configure(self.source, 'http://localhost:8090', 8090, '')
        self.assertEqual((self.source / '.env').read_bytes(), before)
        with self.assertRaisesRegex(ValueError, 'different PUBLIC_BASE_URL'):
            configure(self.source, 'http://127.0.0.1:8090', 8090, '')
        self.assertEqual((self.source / '.env').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
