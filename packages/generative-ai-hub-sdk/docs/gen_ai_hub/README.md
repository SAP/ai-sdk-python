## Configuration for using sdk on SAP AI Core

To configure and use AI Core proxy module follow the steps below:

1. Setup an AI Core account in BTP
2. Retrieve the AI Core service key
3. The following parameters are needed:

- `AICORE_CLIENT_ID`: Client ID
- `AICORE_CLIENT_SECRET`: Client secret
- `AICORE_AUTH_URL`: Url used to retrieve a token using the client id and secret
- `AICORE_BASE_URL`: Url of the service. Use the base url without any additional path
- `AICORE_RESOURCE_GROUP`: Resource group that should be used

For using X.509 credentials, you can set the file paths to certificate and key files, or certificate and key strings, 
as an alternative to client secret.
- `AICORE_CERT_FILE_PATH`: This is the path to the file which holds the X.509 certificate
- `AICORE_KEY_FILE_PATH`: This is the path to the file which holds the X.509 key
- `AICORE_CERT_STR`: This is the content of the X.509 certificate as a string
- `AICORE_KEY_STR`: This is the content of the X.509 key as a string

The values can be set as environment variables are through config files. For most cases we recommend to used config files.
The config files should be placed in AI Core home folder. Which can be set using the env var `AICORE_HOME`, it is set to 
`~/.aicore`, by default.

To fetch the values from config file instead of setting environment variables, create a config under path `<AICORE_HOME>/config.json`
```json
    {
  "AICORE_AUTH_URL": "https://* * * .authentication.sap.hana.ondemand.com/oauth/token",
  "AICORE_CLIENT_ID": "* * * ",
  "AICORE_CLIENT_SECRET": "* * * ",
  "AICORE_RESOURCE_GROUP": "* * * ",
  "AICORE_BASE_URL": "https://api.ai.* * *.cfapps.sap.hana.ondemand.com/v2"
}
```

or

```json
    {
  "AICORE_AUTH_URL": "https://* * * .authentication.cert.sap.hana.ondemand.com",
  "AICORE_CLIENT_ID": "* * * ",
  "AICORE_CERT_FILE_PATH": "* * */cert.pem",
  "AICORE_KEY_FILE_PATH": "* * */key.pem",
  "AICORE_RESOURCE_GROUP": "* * * ",
  "AICORE_BASE_URL": "https://api.ai.* * *.cfapps.sap.hana.ondemand.com/v2"
}
```

or

```json
    {
  "AICORE_AUTH_URL": "https://* * * .authentication.cert.sap.hana.ondemand.com",
  "AICORE_CLIENT_ID": "* * * ",
  "AICORE_CERT_STR": "* * *",
  "AICORE_KEY_STR": "* * *",
  "AICORE_RESOURCE_GROUP": "* * * ",
  "AICORE_BASE_URL": "https://api.ai.* * *.cfapps.sap.hana.ondemand.com/v2"
}
```

You can use the command `aicore configure` to create the needed config file. Use `aicore configure --help` to know various options available.

See full details of client configuration in the [ai-core-sdk documentation](https://github.wdf.sap.corp/AI/ai-core-sdk/blob/master/PYPIDESCRIPTION.md#client-configuration).

### Recommended Way: Download key file and use `aicore configure -k <key-file>`

The easiest way to create a config is to download the key file from BTP and
call `aicore configure -k <key-file>`.

### Using Multiple Different Profiles

The default config is expected to be called `config.json`. To use different service keys for different application
one can create separate profiles. The config for a profile has to be called `<AICORE_HOME>/config_{profile name}.json`.
The profiles can be selected via the environment variable `AICORE_PROFILE`. For example to create a profile `dox`
one has to create the file `<AICORE_HOME>/config_dox.json` and set `AICORE_PROFILE=dox`.

To create a config file for a profile use `aicore -p <profile-name> configure -k <key-file>` Eg. `aicore -p dox configure -k key.json`
