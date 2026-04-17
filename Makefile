MKDIR_P = mkdir -p

jenkins-unit-test:
	${MKDIR_P} ${UNITTEST_OUTPUT_DIR}
	pytest -p pytest_cov --cov=./gen_ai_hub --cov-report xml:coverage.xml --junit-xml=${UNITTEST_OUTPUT_DIR}/unit_tests.xml --verbosity=2 -ra --disable-warnings tests

jenkins-component-test:
	echo "run only acceptance tests"

run-acceptance-test:
	${MKDIR_P} ${ACCEPTANCETEST_OUTPUT_DIR}
	AICORE_RESOURCE_GROUP=gen-ai-hub-sdk pytest --cov=./gen_ai_hub --junit-xml=${ACCEPTANCETEST_OUTPUT_DIR}/report_core.xml --verbosity=2 -ra --disable-warnings integration_tests -m "not bedrock"

run-acceptance-test-us10:
	${MKDIR_P} ${ACCEPTANCETEST_OUTPUT_DIR}
	AICORE_RESOURCE_GROUP=default pytest --cov=./gen_ai_hub --junit-xml=${ACCEPTANCETEST_OUTPUT_DIR}/report_core_us10.xml --verbosity=2 -ra --disable-warnings integration_tests -m bedrock
