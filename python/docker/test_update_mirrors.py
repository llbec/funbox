import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import update_mirrors as app

PAGE = '''# DockerHub
https://unrelated.example
## DockerHub国内镜像加速源列表
| DockerHub镜像仓库 | 镜像加速器地址 |
| --- | --- |
| [首页](https://home.example) | `https://one.example/` |
| name | `two.example` |
| duplicate | `https://one.example` |
| dead | ~~`https://dead.example`~~ |
### 已失效DockerHub加速镜像仓库
| dead | `https://old.example` |
'''


class Tests(unittest.TestCase):
    def test_extract(self):
        self.assertEqual(app.extract_mirrors(PAGE), ['https://one.example', 'https://two.example'])

    def test_limit_and_unreachable(self):
        with patch.object(app, 'check_mirror', side_effect=lambda u, t: (u != '0', 'test')):
            self.assertEqual(app.select_mirrors([str(i) for i in range(8)], 1), ['1', '2', '3', '4', '5'])

    def test_backup_and_fewer_than_five(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'daemon.json'
            original = b'{"debug":true,"log-driver":"json-file","registry-mirrors":["old"]}'
            config.write_bytes(original)
            config.chmod(0o640)
            with patch.object(app, 'fetch_readme', return_value=PAGE), patch.object(app, 'check_mirror', return_value=(True, 'test')):
                self.assertEqual(len(app.update(config)), 2)
            result = json.loads(config.read_text())
            self.assertTrue(result['debug'])
            self.assertEqual(result['log-driver'], 'json-file')
            self.assertEqual(len(result['registry-mirrors']), 2)
            backup = list(Path(directory).glob('*.daemon.json'))
            self.assertEqual(len(backup), 1)
            self.assertRegex(backup[0].name, r'^\d{14}\.daemon\.json$')
            self.assertEqual(backup[0].read_bytes(), original)
            self.assertEqual(config.stat().st_mode & 0o777, 0o640)

    def test_failures_preserve_original(self):
        for original, page, ok in [(b'{}', PAGE, False), (b'{}', '', True), (b'invalid', PAGE, True)]:
            with self.subTest(original=original, page=page), tempfile.TemporaryDirectory() as directory:
                config = Path(directory) / 'daemon.json'
                config.write_bytes(original)
                with patch.object(app, 'fetch_readme', return_value=page), patch.object(app, 'check_mirror', return_value=(ok, 'test')):
                    with self.assertRaises(ValueError):
                        app.update(config)
                self.assertEqual(config.read_bytes(), original)

    def test_duplicate_json_fields(self):
        with self.assertRaises(ValueError):
            json.loads('{"debug":true,"debug":false}', object_pairs_hook=app.unique_object)

    def test_registry_vs_html(self):
        from io import BytesIO
        from urllib.error import HTTPError
        from email.message import Message
        headers = Message()
        headers['WWW-Authenticate'] = 'Bearer realm="https://auth.example"'
        with patch.object(app, 'urlopen', side_effect=HTTPError('https://x/v2/', 401, '', headers, BytesIO(b'{}'))):
            self.assertTrue(app.check_mirror('https://x', 1)[0])
        from unittest.mock import MagicMock
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.headers = {}
        response.read.return_value = b'<html>not a registry</html>'
        with patch.object(app, 'urlopen', return_value=response):
            self.assertFalse(app.check_mirror('https://x', 1)[0])


if __name__ == '__main__':
    unittest.main()
