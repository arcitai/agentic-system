import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("publish", ROOT / "scripts/publish.py")
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


class FakeTable:
    """In-memory stand-in for the public status table, with injected failures per (operation, key)."""

    def __init__(self, public=200):
        self.rows, self.next, self.failures, self.public, self.writes = {}, 0, {}, public, []

    def _fail(self, operation, key, apply):
        mode = self.failures.get((operation, key), [None]).pop(0) if self.failures.get((operation, key)) else None
        if mode == "access":
            raise publish.AccessError("HTTP 401 (expired)")
        if mode == "lost":
            raise publish.UncertainWrite("timeout before apply")
        apply()
        if mode == "applied":
            raise publish.UncertainWrite("timeout after apply")

    def query(self, key):
        self._fail("query", key, lambda: None)
        return [{"id": i, **{f: r.get(f, "") for f in publish.FIELDS}} for i, r in self.rows.items() if r["key"] == key]

    def create(self, key, row):
        def apply():
            self.next += 1
            self.rows[f"row{self.next}"] = {"key": key, **{f: str(v) for f, v in row.items()}}
            self.writes.append(("create", key))
        self._fail("create", key, apply)

    def update(self, row_id, key, row):
        def apply():
            self.rows[row_id].update({f: str(v) for f, v in row.items()})
            self.writes.append(("update", key))
        self._fail("update", key, apply)

    def anonymous_status(self):
        return self.public

    def state(self, key):
        return [r for r in self.rows.values() if r["key"] == key]


def rows(summary_suffix=""):
    out = [{"key": "status/release", "label": "main-working", "summary": "Main working 0.1.33" + summary_suffix, "commit": "c1"},
           {"key": "skill/factory-review", "label": "released-reference", "summary": "released-reference 0.1.18", "commit": "c1"}]
    for row in out:
        row["hash"] = str(hash((row["key"], row["summary"])))
    return out


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.lock = Path(self.temporary.name) / "lock"

    def tearDown(self):
        self.temporary.cleanup()

    def marker(self, table):
        (row,) = table.state(publish.MARKER)
        return row["propagation"].split()[0]

    def test_first_delivery_creates_rows_and_marks_complete_after_readback(self):
        table = FakeTable()
        result = publish.run(rows(), table, self.lock)
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(len(table.state("status/release")), 1)
        self.assertEqual(self.marker(table), "complete")
        self.assertFalse(self.lock.exists())

    def test_repeat_delivery_is_a_no_op(self):
        table = FakeTable()
        publish.run(rows(), table, self.lock)
        before = list(table.writes)
        result = publish.run(rows(), table, self.lock)
        self.assertEqual(result["result"], "NO-OP")
        self.assertEqual([w for w in table.writes[len(before):] if w[1] != publish.MARKER], [])

    def test_changed_source_updates_only_its_key(self):
        table = FakeTable()
        publish.run(rows(), table, self.lock)
        before = len(table.writes)
        result = publish.run(rows(" (changed)"), table, self.lock)
        self.assertEqual(result["changed"], ["status/release"])
        self.assertEqual([w for w in table.writes[before:] if w[1] != publish.MARKER], [("update", "status/release")])

    def test_uncertain_write_that_was_applied_is_read_back_not_duplicated(self):
        table = FakeTable()
        table.failures[("create", "status/release")] = ["applied"]
        result = publish.run(rows(), table, self.lock)
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(len(table.state("status/release")), 1)
        self.assertIn({"key": "status/release", "action": "confirmed-after-uncertain-write"}, result["log"])

    def test_lost_write_is_retried_once_with_the_same_identity(self):
        table = FakeTable()
        publish.run(rows(), table, self.lock)
        table.failures[("update", "status/release")] = ["lost"]
        result = publish.run(rows(" (changed)"), table, self.lock)
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(len(table.state("status/release")), 1)
        self.assertTrue(table.state("status/release")[0]["summary"].endswith("(changed)"))

    def test_partial_update_stays_visible_and_a_later_run_resumes(self):
        table = FakeTable()
        table.failures[("create", "skill/factory-review")] = ["lost", "lost"]
        result = publish.run(rows(), table, self.lock)
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(self.marker(table), "failed")
        self.assertEqual(len(table.state("status/release")), 1)  # applied part kept, not rolled back or deleted
        result = publish.run(rows(), table, self.lock)
        self.assertEqual((result["result"], result["changed"]), ("PUBLISHED", ["skill/factory-review"]))
        self.assertEqual(self.marker(table), "complete")

    def test_expired_access_stops_the_run_and_leaves_pending_visible(self):
        table = FakeTable()
        table.failures[("create", "status/release")] = ["access"]
        result = publish.run(rows(), table, self.lock)
        self.assertEqual(result["result"], "FAILED-ACCESS")
        self.assertEqual(self.marker(table), "pending")
        self.assertEqual(table.state("skill/factory-review"), [])
        self.assertFalse(self.lock.exists())

    def test_duplicate_keys_stop_without_deleting(self):
        table = FakeTable()
        publish.run(rows(), table, self.lock)
        table.rows["dup"] = dict(table.state("status/release")[0])
        result = publish.run(rows(" (changed)"), table, self.lock)
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(len(table.state("status/release")), 2)

    def test_duplicate_marker_rows_also_stop_without_deleting(self):
        table = FakeTable()
        publish.run(rows(), table, self.lock)
        table.rows["dup-marker"] = dict(table.state(publish.MARKER)[0])
        result = publish.run(rows(" (changed)"), table, self.lock)
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(len(table.state(publish.MARKER)), 2)
        self.assertFalse(table.state("status/release")[0]["summary"].endswith("(changed)"))

    def test_incomplete_public_readback_is_not_complete(self):
        table = FakeTable(public=403)
        result = publish.run(rows(), table, self.lock)
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(self.marker(table), "failed")

    def test_concurrent_run_is_refused(self):
        self.lock.write_text("held")
        table = FakeTable()
        self.assertEqual(publish.run(rows(), table, self.lock)["result"], "BUSY")
        self.assertEqual(table.rows, {})

    def test_live_mode_without_dedicated_connection_reports_missing_setup(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_PUBLIC_DOCS_")}
        env["FACTORY_NOTION_TOKEN"] = "must-not-be-used"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/publish.py"), "--live"], cwd=ROOT, env=env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn("not configured: FACTORY_PUBLIC_DOCS_TOKEN", result.stdout)
        self.assertNotIn("must-not-be-used", result.stdout + result.stderr)

    def test_plan_writes_nothing_and_contains_only_projection_keys(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/publish.py")], cwd=ROOT, capture_output=True, text=True, check=True)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["result"], "PLAN")
        self.assertFalse([r["key"] for r in plan["rows"] if r["key"].startswith(("guide/", "declaration/"))])


if __name__ == "__main__":
    unittest.main()
