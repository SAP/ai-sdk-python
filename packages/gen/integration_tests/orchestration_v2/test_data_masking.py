import json
import os
import tempfile

from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.data_masking import (MaskingModuleConfig, MaskingProviderConfig, MaskingMethod,
                                                             DPIStandardEntity, ProfileEntity, MaskFileInputMethod)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.multimodal_items import FileItem
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestDataMasking(OrchestrationServiceTestBase):

    # Person name embedded in the PDF fixture used by the file-input masking tests.
    pdf_person_name = "Maximillian"

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.pdf_path = os.path.join(cls.temp_dir.name, "test_doc.pdf")
        cls._write_minimal_pdf(
            cls.pdf_path,
            f"Please contact {cls.pdf_person_name} at {cls.pdf_person_name}@example.com.",
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    @classmethod
    def _write_minimal_pdf(cls, path: str, text: str) -> None:
        stream_content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
        parts = [
            b"%PDF-1.4",
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj",
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj",
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
            b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>\nendobj",
            b"4 0 obj<</Length " + str(len(stream_content)).encode() + b">>\nstream\n"
            + stream_content + b"\nendstream\nendobj",
            b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj",
        ]
        buf = b""
        offsets = []
        for part in parts:
            offsets.append(len(buf))
            buf += part + b"\n"
        xref_pos = len(buf)
        buf += b"xref\n0 6\n" + b"0000000000 65535 f \n"
        for off in offsets:
            buf += f"{off:010d} 00000 n \n".encode()
        buf += b"trailer<</Size 6/Root 1 0 R>>\nstartxref\n" + str(xref_pos).encode() + b"\n%%EOF"
        with open(path, "wb") as f:
            f.write(buf)

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLMModelDetails(
            name="gpt-4o",
            params={
                'temperature': 0.0,
            }
        )
        # Gemini is used for file inputs, matching the multimodal templating tests.
        self.file_llm = LLMModelDetails(
            name="gemini-2.5-flash",
            version="latest",
            params={
                "max_tokens": 50,
                "temperature": 0.0,
            },
        )
        self.template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ]
        )
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=self.llm)

    def _run_file_masking(self, mask_file_input_method: MaskFileInputMethod):
        file_item = FileItem.from_file(self.pdf_path, filename="test_doc.pdf")

        data_masking_config = MaskingModuleConfig(
            providers=[MaskingProviderConfig(
                method=MaskingMethod.ANONYMIZATION,
                entities=[
                    DPIStandardEntity(type=ProfileEntity.PERSON),
                    DPIStandardEntity(type=ProfileEntity.EMAIL),
                ],
                mask_file_input_method=mask_file_input_method,
            )],
        )

        template = Template(template=[
            SystemMessage(content="You are a helpful AI assistant."),
            UserMessage(content=[
                file_item,
                "What is the full name of the person mentioned in this document? "
                "Reply with only the name.",
            ]),
        ])
        prompt_template = PromptTemplatingModuleConfig(prompt=template, model=self.file_llm)
        module_config = ModuleConfig(prompt_templating=prompt_template, masking=data_masking_config)
        config = OrchestrationConfig(modules=module_config)

        return self.service.run(config=config)

    def test_data_masking_test(self):
        data_masking_config = MaskingModuleConfig(
            providers=[MaskingProviderConfig(
                method=MaskingMethod.PSEUDONYMIZATION,
                entities=[DPIStandardEntity(type=ProfileEntity.EMAIL)]
            )]
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, masking=data_masking_config)

        config = OrchestrationConfig(modules=module_config)

        sensitive_data = "something@hotmail.com"

        response = self.service.run(config=config,
                                    placeholder_values={"user_query": f"My email is {sensitive_data}"
                                                                    f"-----------------------------------"
                                                                    f"DON'T check if anything is masked, "
                                                                    f"repeat the previous sentence."
                                                                    f"DON'T alter the format of the "
                                                                    f"masked data."
                                                        }
                                    )

        self.assertIsNot(sensitive_data, response.final_result.choices[0].message.content)
        self.assertIsNotNone(response.intermediate_results.input_masking)

    def test_data_masking_file_input_anonymization(self):
        response = self._run_file_masking(MaskFileInputMethod.ANONYMIZATION)

        self.assertIsNotNone(response.intermediate_results.input_masking)
        # The person name in the file is anonymized before reaching the model,
        # so it must not be echoed back in the completion.
        self.assertNotIn(
            self.pdf_person_name.upper(),
            response.final_result.choices[0].message.content.upper(),
        )

    def test_data_masking_file_input_skip(self):
        response = self._run_file_masking(MaskFileInputMethod.SKIP)

        # File inputs are left unmasked, so the model can still read the person name.
        self.assertIn(
            self.pdf_person_name.upper(),
            response.final_result.choices[0].message.content.upper(),
        )

    def test_data_masking_with_allowlist(self):
        allow_listed_org = "SAP"
        data_masking_config = MaskingModuleConfig(
           providers=[MaskingProviderConfig(
                method=MaskingMethod.PSEUDONYMIZATION,
                entities=[DPIStandardEntity(type=ProfileEntity.ORG)],
                allowlist=[allow_listed_org]
            )]
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, masking=data_masking_config)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(
            config=config,
            placeholder_values={"user_query": f"My organisation is {allow_listed_org}"}
        )

        # Verify that the allow-listed org is present in the masked template
        masked_template = json.loads(response.intermediate_results.input_masking.data['masked_template'])
        self.assertIn(allow_listed_org, masked_template[1]['content'],
                      f"Allow-listed organization '{allow_listed_org}' should not be masked")

    def test_data_masking_test_backward_compatibility(self):
        data_masking_config = MaskingModuleConfig(
            masking_providers=[MaskingProviderConfig(
                method=MaskingMethod.PSEUDONYMIZATION,
                entities=[DPIStandardEntity(type=ProfileEntity.EMAIL)]
            )]
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, masking=data_masking_config)

        config = OrchestrationConfig(modules=module_config)

        sensitive_data = "something@hotmail.com"

        response = self.service.run(config=config,
                                    placeholder_values={"user_query": f"My email is {sensitive_data}"
                                                                      f"-----------------------------------"
                                                                      f"DON'T check if anything is masked, "
                                                                      f"repeat the previous sentence."
                                                                      f"DON'T alter the format of the "
                                                                      f"masked data."
                                                        }
                                    )

        self.assertIsNot(sensitive_data, response.final_result.choices[0].message.content)
        self.assertIsNotNone(response.intermediate_results.input_masking)
