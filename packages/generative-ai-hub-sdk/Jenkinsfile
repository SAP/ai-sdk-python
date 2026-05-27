#!/usr/bin/env groovy

AIF_TOOLKIT_VERSION='master'

library "piper-lib"
library "piper-lib-os"
library "AIF_CICD_Toolkit@${AIF_TOOLKIT_VERSION}"

executeAIFPipeline(branch: 'main', libraryVersion: "${AIF_TOOLKIT_VERSION}", stagesToExclude: ['Run ClamAV Malware Scan','Run Component Test', 'Run Checkmarx Scan', 'Run Whitesource Scan', 'PPMS Whitesource Compliance', 'Validate Swagger with Contract', 'Verify Provider', 'Verify Consumer Contract as Provider'])
