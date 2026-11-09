import tempfile
import unittest

from fastapi.testclient import TestClient

from systems import api
from systems.generator import main

KEY = {"X-API-Key": api.API_KEY}


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        out = tempfile.mkdtemp()
        main(["history", "--days", "2", "--scale", "0.5", "--out", out])
        api.DATA = api.Path(out)
        cls.client = TestClient(api.app)

    def setUp(self):
        api.recent.clear()

    def test_needs_key(self):
        self.assertEqual(self.client.get("/orders", params={"date": "2025-11-01"}).status_code, 401)
        self.assertEqual(self.client.get("/health").status_code, 200)

    def test_pages_cover_every_order_once(self):
        seen, page = [], 1
        while page:
            body = self.client.get("/orders", params={"date": "2025-11-01", "page": page, "page_size": 7}, headers=KEY).json()
            seen += [o["order_id"] for o in body["data"]]
            page = body["next_page"]
        self.assertEqual(len(seen), body["total"])
        self.assertEqual(len(seen), len(set(seen)))

    def test_unknown_day_is_empty(self):
        body = self.client.get("/orders", params={"date": "2020-01-01"}, headers=KEY).json()
        self.assertEqual((body["total"], body["data"], body["next_page"]), (0, [], None))

    def test_single_order(self):
        first = self.client.get("/orders", params={"date": "2025-11-02"}, headers=KEY).json()["data"][0]
        self.assertEqual(self.client.get(f"/orders/{first['order_id']}", headers=KEY).json(), first)
        self.assertEqual(self.client.get("/orders/WEB-nope", headers=KEY).status_code, 404)

    def test_rate_limit(self):
        codes = [self.client.get("/orders", params={"date": "2025-11-01"}, headers=KEY).status_code for _ in range(api.RATE_LIMIT + 1)]
        self.assertEqual(codes[-1], 429)
        self.assertTrue(all(c == 200 for c in codes[:-1]))


if __name__ == "__main__":
    unittest.main()
