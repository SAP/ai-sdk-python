from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EModel(AIAPIV2ClientE2ETestBase):
    def test_query_models(self):
        res = self.ai_api_v2_client.model.query()
        self.assertEqual(res.count, len(res.resources))
        self.assertGreater(res.count, 0)
        model = res.resources[0]

        self.assertIsNotNone(model.executable_id)
        self.assertIsNotNone(model.model)
        self.assertIsNotNone(model.description)
        self.assertIsNotNone(model.versions)
