"""The release must contain current, intact, domain-audited calculator files."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from tivars.models import TI_84PCE
from tools.build import tokenize_source
from tools import package


class PackageVerification(TestCase):
    def prepare(self, root, source='Stop', binary_source=None):
        (root/'src').mkdir()
        (root/'src/TEST.txt').write_text(source+'\n', encoding='utf-8')
        target = root/'TEST.8xp'
        program = tokenize_source(source if binary_source is None else binary_source, 'TEST')
        program.save(str(target), model=TI_84PCE)
        return target

    def test_current_program_passes_but_stale_or_misnamed_program_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = self.prepare(root)
            with patch.object(package, 'ROOT', root):
                package.verify_programs([target])
                (root/'src/TEST.txt').write_text('ClrHome\nStop\n', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'stale binary'):
                    package.verify_programs([target])
                (root/'src/TEST.txt').write_text('Stop\n', encoding='utf-8')
                wrong_name = tokenize_source('Stop', 'OTHER')
                wrong_name.save(str(target), model=TI_84PCE)
                with self.assertRaisesRegex(ValueError, 'program name'):
                    package.verify_programs([target])

    def test_corrupt_container_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = self.prepare(root)
            raw = bytearray(target.read_bytes())
            raw[-1] ^= 1
            target.write_bytes(raw)
            with patch.object(package, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'checksum'):
                    package.verify_programs([target])

    def test_matching_bad_footer_is_rejected_before_packaging(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = self.prepare(root, 'Text(156,6,"R3 FOOTER")')
            with patch.object(package, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'Text row'):
                    package.verify_programs([target])
