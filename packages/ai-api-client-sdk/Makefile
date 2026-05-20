MKDIR_P = mkdir -p

jenkins-unit-test:
	${MKDIR_P} ${UNITTEST_OUTPUT_DIR}
	pytest -p pytest_cov --cov=./ai_api_client_sdk --cov-report xml:coverage.xml --junit-xml=${UNITTEST_OUTPUT_DIR}/unit_tests.xml --verbosity=2 -ra --disable-warnings tests

jenkins-component-test:
	${MKDIR_P} ${COMPONENTTEST_OUTPUT_DIR}
	pytest -p pytest_cov --cov=./ai_api_client_sdk --junit-xml=${COMPONENTTEST_OUTPUT_DIR}/component_tests.xml --verbosity=2 -ra --disable-warnings integration_tests

jenkins-contract-test:
	echo "Contract Test Stage"

run-acceptance-test:
	${MKDIR_P} ${ACCEPTANCETEST_OUTPUT_DIR}
	pytest -p pytest_cov --cov=./ai_api_client_sdk --junit-xml=${ACCEPTANCETEST_OUTPUT_DIR}/acceptance_tests.xml --verbosity=2 -ra --disable-warnings integration_tests