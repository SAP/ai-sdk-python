#!/usr/bin/env bash

# Available env variables
# TARGET_REPO_FOLDER: Foldername in Jenkins workspace where target repository has been cloned to. Should be used to update the respective files with the script.
# APPLICATION_VERSION: Calculated version of the current application build. This corresponds to the promoted version by the build.
# SOURCE_BRANCH: Corresponds to the current branch we run.
# TARGET_BRANCH: Corresponds to the target branch we want to raise a PR against.

function main() {
  src_base_test="acceptance_tests/aicore-content"
  src_acceptance_test_template_base="$src_base_test/test-templates"
  src_test_content="$src_base_test/test-content"
  tgt_base="$TARGET_REPO_FOLDER/services/ai-core-sdk/source"
  tgt_test_template_base="$tgt_base/test/template"
  tgt_acceptance_test_template_base="$tgt_test_template_base/ai-core-sdk-acceptance-test"
  tgt_test_content="$tgt_base/test/content"

  chart_file="Chart.yaml"
  chartbak_file="Chart.yamlbak"
  values_file="values.yaml"
  template_file="templates/wft-acceptance-tests.yaml"

  version_pattern="s/(^[ \t]*)version:[ ]{1,}([0-9]{1,4}\.){2}[0-9]{1,4}$/\1version: $APPLICATION_VERSION/"

  sed -ibak -E "${version_pattern}" "${tgt_test_content}/${chart_file}"
  rm -f ${tgt_test_content}/${chartbak_file}
  sed -ibak -E "${version_pattern}" "${tgt_acceptance_test_template_base}/${chart_file}"
  rm -f ${tgt_acceptance_test_template_base}/${chartbak_file}

  cp -R ${src_test_content}/templates/* "${tgt_test_content}/templates"
  cp -R "${src_test_content}/${values_file}" "${tgt_test_content}/${values_file}"
  cp -R "${src_acceptance_test_template_base}/${values_file}" "${tgt_acceptance_test_template_base}/${values_file}"
  cp -R "${src_acceptance_test_template_base}/${template_file}" "${tgt_acceptance_test_template_base}/${template_file}"
}

main