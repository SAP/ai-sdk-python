import unittest

from gen_ai_hub.orchestration.models.template_ref import TemplateRef


class TestTemplateRef(unittest.TestCase):

    def test_creates_instance_from_id(self):
        template_ref = TemplateRef.from_id(prompt_template_id="test_template_id")
        self.assertEqual(template_ref.id, "test_template_id")
        self.assertEqual(template_ref.to_dict(), {"template_ref": {"id": "test_template_id"}})

    def test_creates_instance_from_tuple(self):
        template_ref = TemplateRef.from_tuple("test_scenario", "test_name", "test_version")
        self.assertEqual(template_ref.scenario, "test_scenario")
        self.assertEqual(template_ref.name, "test_name")
        self.assertEqual(template_ref.version, "test_version")
        self.assertEqual(template_ref.to_dict(), {"template_ref":
                                                      {"scenario": "test_scenario",
                                                       "name": "test_name",
                                                       "version": "test_version"}
                                                  }
                         )

    def test_handles_kwargs(self):
        template_ref = TemplateRef(id="test_template_id")
        self.assertEqual(template_ref.to_dict(), {"template_ref": {"id": "test_template_id"}})

        template_ref = TemplateRef(scenario="test_scenario", name="test_name", version="test_version")
        self.assertEqual(template_ref.to_dict(), {"template_ref":
                                                      {"scenario": "test_scenario",
                                                       "name": "test_name",
                                                       "version": "test_version"}
                                                  }
                         )
