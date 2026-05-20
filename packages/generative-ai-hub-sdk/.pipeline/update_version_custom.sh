pip3 install --trusted-host int.repositories.cloud.sap --trusted-host github.wdf.sap.corp --index-url https://int.repositories.cloud.sap/artifactory/api/pypi/build-snapshots-pypi/simple -r requirements.txt
pydoc3 -w ./
mv gen_ai_hub*.html docs/
rm *.html
echo "------ update version to $1 -----"
echo "$1" > acceptance_tests/cfg/VERSION