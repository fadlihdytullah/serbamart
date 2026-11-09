import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from systems.generator import main


def tree(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(Path(root).rglob("*")) if p.is_file()
    }


def pos_lines(root):
    return [row for f in sorted(Path(root, "pos").rglob("*.csv")) for row in csv.DictReader(f.read_text().splitlines())]


class GeneratorTest(unittest.TestCase):
    def run_cli(self, *args):
        out = tempfile.mkdtemp()
        main([*args[0], "--out", out])
        for extra in args[1:]:
            main([*extra, "--out", out])
        return out

    def test_same_seed_same_data(self):
        a = self.run_cli(["history", "--days", "3", "--scale", "0.2"])
        b = self.run_cli(["history", "--days", "3", "--scale", "0.2"])
        self.assertEqual(tree(a), tree(b))

    def test_next_day_matches_longer_history(self):
        a = self.run_cli(["history", "--days", "4", "--scale", "0.2", "--issues", "all"])
        b = self.run_cli(["history", "--days", "3", "--scale", "0.2", "--issues", "all"], ["next-day"])
        self.assertEqual(tree(a), tree(b))

    def test_clean_data_has_no_issues(self):
        rows = pos_lines(self.run_cli(["history", "--days", "5", "--scale", "0.5"]))
        self.assertTrue(all(r["sold_at"][-6] in "+-" for r in rows))
        self.assertTrue(all(r["qty"].isdigit() and r["unit_price"].isdigit() and r["payment_method"] for r in rows))
        self.assertEqual(len(rows), len({tuple(r.values()) for r in rows}))

    def test_issues_keep_the_base_sales(self):
        clean = self.run_cli(["history", "--days", "5", "--scale", "0.5"])
        messy = self.run_cli(["history", "--days", "5", "--scale", "0.5", "--issues", "duplicates,bad-types,nulls"])
        key = lambda r: (r["transaction_id"], r["sku"])
        clean_keys = {key(r) for r in pos_lines(clean)}
        messy_rows = pos_lines(messy)
        self.assertEqual(clean_keys, {key(r) for r in messy_rows})
        self.assertGreater(len(messy_rows), len(clean_keys))
        self.assertTrue(any(r["unit_price"].startswith("Rp") for r in messy_rows))
        self.assertTrue(any(r["payment_method"] == "" for r in messy_rows))

    def test_late_files_arrive_later(self):
        out = self.run_cli(["history", "--days", "30", "--scale", "0.2", "--issues", "late-files"])
        late = [f for f in Path(out, "pos").rglob("*.csv") if f.parent.name != f.stem.split("_")[1]]
        self.assertTrue(late)
        self.assertTrue(all(f.parent.name > f.stem.split("_")[1] for f in late))

    def test_prices_rise_after_enabling(self):
        out = self.run_cli(["history", "--days", "120", "--scale", "0.1", "--issues", "price-changes"])
        products = list(csv.DictReader(Path(out, "products.csv").read_text().splitlines()))
        self.assertTrue(any(r["updated_on"] != "2025-11-01" for r in products))


if __name__ == "__main__":
    unittest.main()
