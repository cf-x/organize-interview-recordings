"""Synthetic regression fixtures; never use real interview material."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from test_scripts import SKILL_ROOT, VALID_NOTE, load_module

SCRIPTS = SKILL_ROOT / 'scripts'


class IncrementalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                              capture_output=True, text=True)

    def note(self, text=VALID_NOTE):
        path = self.root / '20260807-example.md'
        path.write_text(text)
        return path

    def audit(self, *args):
        return self.run_script('audit_interview_notes.py', self.root, '--require-purple-ai', *args)

    def test_empty_directory_fails(self):
        self.assertNotEqual(self.audit().returncode, 0)

    def test_no_questions_fails(self):
        self.note(VALID_NOTE.split('### 1.')[0] + '## 面试总结\n')
        self.assertIn('no question blocks', self.audit().stdout)

    def test_missing_anchor_fails(self):
        self.note(VALID_NOTE + '\n[example](20260807-example.md#missing)\n')
        self.assertIn('missing link anchor', self.audit().stdout)

    def test_empty_summary_fails(self):
        self.note(VALID_NOTE.replace('**主要问题：** 证据不足', '**主要问题：**'))
        self.assertIn('empty summary field', self.audit().stdout)

    def test_changed_collection_anchor_is_checked(self):
        self.note()
        extra = self.root / 'topic.md'
        extra.write_text('[broken](20260807-example.md#missing)')
        self.assertNotEqual(self.audit('--links-file', extra).returncode, 0)

    def test_explicit_anchor_passes(self):
        self.note(VALID_NOTE + '\n<a id="example"></a>\n[example](#example)\n')
        self.assertEqual(self.audit().returncode, 0)

    def test_legacy_shape_only_fails_in_strict_mode(self):
        self.note()
        self.assertEqual(self.audit().returncode, 0)
        self.assertNotEqual(self.audit('--require-bullets').returncode, 0)

    def test_keyword_bullets_pass(self):
        self.note(VALID_NOTE.replace('- <span style="color:#7C3AED"><strong>🟣 AI 生成优化回答：</strong></span> 补充约束和证据。', '<span style="color:#7C3AED"><strong>🟣 AI 生成优化回答：</strong></span>\n\n- **约束：** 补充约束和证据。'))
        self.assertEqual(self.audit('--require-bullets').returncode, 0)

    def test_reconstruction_does_not_replace_answer(self):
        self.note(VALID_NOTE.replace('AI 生成优化回答', 'AI 重建问题'))
        self.assertIn('reconstruction alone', self.audit().stdout)

    def test_backup_detects_corruption_and_preserves_original(self):
        note = self.note()
        manifest = self.root / 'backup' / 'manifest.json'
        args = ['--root', self.root, '--manifest', manifest]
        result = self.run_script('workspace_state.py', 'backup', *args, '--file', note.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        note.write_text('edited')
        self.assertEqual(self.run_script('workspace_state.py', 'verify-backup', *args).returncode, 0)
        self.assertEqual((manifest.parent / note.name).read_text(), VALID_NOTE)
        (manifest.parent / note.name).write_text('corrupt')
        self.assertNotEqual(self.run_script('workspace_state.py', 'verify-backup', *args).returncode, 0)

    def test_fingerprint_invalidation(self):
        note = self.note()
        args = ['--root', self.root, '--file', note.name, '--manifest', self.root / 'state.json']
        self.assertEqual(self.run_script('workspace_state.py', 'save', *args).returncode, 0)
        state = json.loads(self.run_script('workspace_state.py', 'check', *args).stdout)
        self.assertTrue(state['unchanged'])
        note.write_text('changed')
        self.assertFalse(json.loads(self.run_script('workspace_state.py', 'check', *args).stdout)['unchanged'])
        self.assertTrue(json.loads(self.run_script('workspace_state.py', 'check', *args, '--version', '2').stdout)['version_changed'])
        note.unlink()
        self.assertNotEqual(self.run_script('workspace_state.py', 'check', *args).returncode, 0)

    def test_merge_preserves_overlap_metadata_and_sources(self):
        merger = load_module('merge_test', SCRIPTS / 'merge_transcripts.py')
        a, b = self.root / 'a.json', self.root / 'b.json'
        a.write_text(json.dumps({'segments': [{'start': 0, 'end': 2, 'text': 'A', 'speaker': 's1'}]}))
        b.write_text(json.dumps({'segments': [{'start': 1, 'end': 3, 'text': 'B'}]}))
        result = merger.merge({'system': a, 'microphone': b}, {})
        self.assertEqual(result['segments'][0]['speaker'], 's1')
        self.assertEqual(result['segments'][1]['start'], 1)
        self.assertEqual(result['segments'][1]['role'], 'microphone')
        args = ['--source', f'system={a}', '--source', f'microphone={b}', '--output', self.root / 'merged']
        self.assertEqual(self.run_script('merge_transcripts.py', *args).returncode, 0)
        self.assertNotEqual(self.run_script('merge_transcripts.py', *args).returncode, 0)
        self.assertEqual(json.loads(a.read_text())['segments'][0]['text'], 'A')

    def test_bad_timestamps_rejected_and_zero_flagged(self):
        merger = load_module('merge_invalid_test', SCRIPTS / 'merge_transcripts.py')
        path = self.root / 'input.json'
        for start, end in [(-1, 2), (2, 1), (0, float('nan')), (0, 200)]:
            path.write_text(json.dumps({'segments': [{'start': start, 'end': end, 'text': 'x'}]}))
            with self.assertRaises(ValueError):
                merger.merge({'source': path}, {}, 100)
        path.write_text(json.dumps({'segments': [{'start': 0, 'end': 0, 'text': 'x'}]}))
        self.assertEqual(merger.merge({'source': path}, {})['qc']['zero_duration_units'], 1)

    def test_catalog_queries_primary_headings(self):
        topic = self.root / 'topic.md'
        topic.write_text('# Topics\n\n## How to evaluate ASR?\n<a id="asr-eval"></a>\nText\n## Other topic\nText\n')
        catalog = self.root / 'catalog.json'
        result = self.run_script('question_catalog.py', 'build', '--root', self.root, '--file', topic.name, '--catalog', catalog)
        self.assertEqual(result.returncode, 0, result.stderr)
        query = self.run_script('question_catalog.py', 'query', '--catalog', catalog, '--text', 'ASR evaluation')
        data = json.loads(query.stdout)
        self.assertEqual(data['candidates'][0]['anchors'], ['asr-eval'])
        self.assertTrue(data['lexical_only'])


if __name__ == '__main__':
    unittest.main()
