package com.sap.ai.sdk.codegen;

/** Keys for the SAP Cloud SDK vendor extensions consumed by {@link SapPythonCodegen}. */
final class SapExtensions {

    private SapExtensions() {}

    /**
     * Sets the API class an operation belongs to. Resolved with a cascade:
     * operation level &gt; path level &gt; root level. A trailing literal "Api" suffix is stripped.
     */
    static final String API_NAME = "x-sap-cloud-sdk-api-name";

    /** Overrides the operation's method name (replaces the derived operationId). */
    static final String OPERATION_NAME = "x-sap-cloud-sdk-operation-name";
}
