# This Dockerfile is used to run the acceptance tests
FROM public.int.repositories.cloud.sap/com.sap.aicore.linuxx86_64/sles-ai-python-compiler:1.8.12

ARG ARTIFACTORY=https://int.repositories.cloud.sap/artifactory/api/pypi/build-releases-pypi/simple/

RUN groupadd -g 999 aicoresdk && \
    useradd --create-home --home-dir /home/aicoresdk --system --uid 1000 --gid aicoresdk aicoresdk

RUN mkdir -p /app/features
COPY . /app/features
RUN mv /app/features/Makefile /app/Makefile
RUN chown -R aicoresdk:aicoresdk /app
WORKDIR /app

RUN pip3 install --no-cache-dir --trusted-host int.repositories.cloud.sap --trusted-host github.wdf.sap.corp --index-url $ARTIFACTORY -r features/requirements-acceptancetest.txt
RUN pip3 install --no-cache-dir -r features/requirements-test.txt
