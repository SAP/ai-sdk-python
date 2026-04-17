import unittest

from gen_ai_hub.orchestration_v2.models.template_ref import TemplateRef, TemplateRefByID, TemplateRefByScenarioNameVersion


class TestTemplateRef(unittest.TestCase):

    def test_creates_instance_from_id(self):
        template_ref = TemplateRef(template_ref=TemplateRefByID(id="test_template_id"))
        self.assertEqual(
            template_ref.model_dump(),
            {"template_ref": {"id": "test_template_id", "scope": "tenant"}})

    def test_creates_instance_from_tuple(self):
        template_ref = TemplateRefByScenarioNameVersion(scenario="test_scenario",
                                                        name="test_name",
                                                        version="test_version",
                                                        scope="resource_group")
        template=TemplateRef(template_ref=template_ref)
        self.assertEqual(template_ref.scenario, "test_scenario")
        self.assertEqual(template_ref.name, "test_name")
        self.assertEqual(template_ref.version, "test_version")
        self.assertEqual(template.model_dump(), {"template_ref":
                                                      {"scenario": "test_scenario",
                                                       "name": "test_name",
                                                       "version": "test_version",
                                                       "scope": "resource_group"}
                                                  }
                         )
    def test_creates_instance_with_unsupported_scope(self):
        with self.assertRaises(ValueError):
            TemplateRefByScenarioNameVersion(scenario="test_scenario",
                                             name="test_name",
                                             version="test_version",
                                             scope="unsupported_scope")