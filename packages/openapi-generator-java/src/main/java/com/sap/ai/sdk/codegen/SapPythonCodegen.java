package com.sap.ai.sdk.codegen;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.Operation;
import io.swagger.v3.oas.models.PathItem;
import io.swagger.v3.oas.models.servers.Server;
import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import org.openapitools.codegen.CodegenModel;
import org.openapitools.codegen.CodegenProperty;
import org.openapitools.codegen.CodegenType;
import org.openapitools.codegen.languages.PythonClientCodegen;
import org.openapitools.codegen.model.ModelMap;
import org.openapitools.codegen.model.ModelsMap;

/**
 * Custom openapi-generator codegen for the SAP Cloud SDK for AI (Python).
 *
 * <p>Extends the stock {@code python} generator ({@link PythonClientCodegen}) and relocates the
 * customizations that the Python SDK previously applied via external pre/post-processing scripts
 * into generator hooks. Registered for {@code -g sap-python} via the ServiceLoader file
 * {@code META-INF/services/org.openapitools.codegen.CodegenConfig}.
 *
 * <p>Implemented so far:
 *
 * <ul>
 *   <li>{@link #setOpenAPI(OpenAPI)} resolves the {@code x-sap-cloud-sdk-api-name} and
 *       {@code x-sap-cloud-sdk-operation-name} vendor extensions. This runs <em>before</em> the
 *       {@code InlineModelResolver} flattens inline request/response schemas, so those schemas are
 *       named from the short SAP operation name rather than the verbose original operationId.
 *   <li>{@link #preprocessOpenAPI(OpenAPI)} injects the configured {@code basePath} into
 *       {@code servers}.
 *   <li>{@link #postProcessAllModels(Map)} rewrites the pydantic field alias from
 *       {@code alias=} to {@code serialization_alias=} (replacing the former regex post-processing).
 *   <li>{@link #modelFilename(String, String)} de-duplicates model filenames on the final
 *       snake_case name rather than the raw model name, preventing the spurious numbered-file
 *       artifact (e.g. {@code filterconditions0.py}) the former {@code _fix_numbered_duplicates}
 *       post-processing had to rename away.
 * </ul>
 *
 * <p>The SAP model shape itself is carried by the bundled {@code sap-python/model_generic.mustache}
 * template override.
 */
public class SapPythonCodegen extends PythonClientCodegen {

    /** Additional-property key carrying the service base path (replaces servers[0].url). */
    static final String BASE_PATH_PROPERTY = "basePath";

    /**
     * Case-insensitive set of model filenames already emitted, tracked on the final snake_case name.
     * Mirrors the generator's own {@code seenModelFilenames} but keys on the post-{@code
     * toModelFilename} name so names that only collide <em>before</em> snake_casing (e.g.
     * {@code FilterConditions} vs {@code Filterconditions}) are not spuriously numbered. Maps the
     * lower-cased filename to itself purely to detect reuse.
     */
    private final Map<String, String> seenSnakeCaseFilenames = new HashMap<>();

    public SapPythonCodegen() {
        super();
    }

    @Override
    public String getName() {
        return "sap-python";
    }

    @Override
    public CodegenType getTag() {
        return CodegenType.CLIENT;
    }

    @Override
    public String getHelp() {
        return "Generates a Python client for the SAP Cloud SDK for AI "
                + "(customized python generator).";
    }

    @Override
    public void setOpenAPI(OpenAPI openAPI) {
        // Resolve the SAP vendor extensions BEFORE super stores the spec and, crucially, before
        // the generator's InlineModelResolver runs (which names inline schemas from operationId).
        applyApiNameExtension(openAPI);
        applyOperationNameExtension(openAPI);
        super.setOpenAPI(openAPI);
    }

    @Override
    public void preprocessOpenAPI(OpenAPI openAPI) {
        applyBasePath(openAPI);
        super.preprocessOpenAPI(openAPI);
    }

    @Override
    public Map<String, ModelsMap> postProcessAllModels(Map<String, ModelsMap> objs) {
        Map<String, ModelsMap> result = super.postProcessAllModels(objs);
        for (ModelsMap modelsMap : result.values()) {
            for (ModelMap modelMap : modelsMap.getModels()) {
                CodegenModel model = modelMap.getModel();
                if (model == null) {
                    continue;
                }
                rewriteAliasToSerializationAlias(model.vars);
                rewriteAliasToSerializationAlias(model.allVars);
            }
        }
        return result;
    }

    // ------------------------------------------------------------------
    // model filename de-duplication (prevents the fileN.py collision artifact)
    // ------------------------------------------------------------------

    /**
     * Computes a model's output filename, de-duplicating on the <em>final</em> snake_case name.
     *
     * <p>The stock {@link org.openapitools.codegen.DefaultCodegen#modelFilename(String, String)}
     * uniquifies case-insensitively on the <em>raw</em> model name <em>before</em> snake_casing it.
     * Two distinct schemas that differ only in case (here {@code FilterConditions} and the
     * title-named inline model {@code Filterconditions}) are therefore treated as a collision: the
     * second is renamed {@code Filterconditions0}, yielding {@code filterconditions0.py}. But their
     * class names and imports derive from {@code toModelName}, which does <em>not</em> add the
     * suffix, so the import references {@code filterconditions} — a file that never exists. The
     * former Python {@code _fix_numbered_duplicates} step papered over this by renaming the file.
     *
     * <p>Snake_casing resolves the names to genuinely distinct files ({@code filter_conditions.py}
     * vs {@code filterconditions.py}), so uniquifying on the snake_case name instead removes the
     * spurious suffix while still numbering any <em>real</em> filename collision.
     */
    @Override
    public String modelFilename(String templateName, String modelName) {
        String suffix = modelTemplateFiles().get(templateName);
        String base = toModelFilename(modelName);
        String key = base.toLowerCase(Locale.ROOT);
        if (seenSnakeCaseFilenames.containsKey(key)) {
            // Genuine snake_case collision: fall back to the stock numbered behavior.
            int n = 0;
            String numberedBase;
            String numberedKey;
            do {
                numberedBase = base + n;
                numberedKey = numberedBase.toLowerCase(Locale.ROOT);
                n++;
            } while (seenSnakeCaseFilenames.containsKey(numberedKey));
            base = numberedBase;
            key = numberedKey;
        }
        seenSnakeCaseFilenames.put(key, base);
        return modelFileFolder() + File.separator + base + suffix;
    }

    /**
     * Sets each operation's single tag from {@code x-sap-cloud-sdk-api-name}, resolving with a
     * cascade (operation &gt; path &gt; root) and stripping a trailing literal "Api" suffix.
     * Operations without the extension keep their declared tags.
     */
    private void applyApiNameExtension(OpenAPI openAPI) {
        if (openAPI.getPaths() == null) {
            return;
        }
        String rootName = extensionString(openAPI.getExtensions(), SapExtensions.API_NAME);
        for (PathItem pathItem : openAPI.getPaths().values()) {
            if (pathItem == null) {
                continue;
            }
            String pathName = extensionString(pathItem.getExtensions(), SapExtensions.API_NAME);
            for (Operation op : pathItem.readOperations()) {
                String opName = extensionString(op.getExtensions(), SapExtensions.API_NAME);
                String effective = firstNonNull(opName, pathName, rootName);
                if (effective != null) {
                    op.setTags(Collections.singletonList(stripApiSuffix(effective)));
                }
            }
        }
    }

    /** Remove a trailing literal "Api" suffix (case-sensitive, matching the former Java behavior). */
    static String stripApiSuffix(String name) {
        return name.endsWith("Api") ? name.substring(0, name.length() - 3) : name;
    }

    // ------------------------------------------------------------------
    // x-sap-cloud-sdk-operation-name  ->  operationId (controls the method name)
    // ------------------------------------------------------------------

    /**
     * Overwrites {@code operationId} with {@code x-sap-cloud-sdk-operation-name} where present.
     *
     * <p>OpenAPI requires globally unique operationIds, but two operations in different tags may
     * legitimately want the same method name (e.g. both a Vector and a Retrieval API exposing
     * {@code search}). When a desired name collides across tags, the operationId is scoped to
     * {@code snake(tag)_snake(name)} and an {@code operationIdNameMapping} entry is registered so
     * the generator renders the method with the short desired name inside its class.
     */
    private void applyOperationNameExtension(OpenAPI openAPI) {
        if (openAPI.getPaths() == null) {
            return;
        }

        // First pass: collect desired (operation, name, tag) and count name occurrences.
        List<Operation> ops = new ArrayList<>();
        List<String> names = new ArrayList<>();
        List<String> tags = new ArrayList<>();
        Map<String, Integer> nameCounts = new HashMap<>();
        for (PathItem pathItem : openAPI.getPaths().values()) {
            if (pathItem == null) {
                continue;
            }
            for (Operation op : pathItem.readOperations()) {
                String desired = extensionString(op.getExtensions(), SapExtensions.OPERATION_NAME);
                if (desired == null) {
                    continue;
                }
                String tag =
                        (op.getTags() != null && !op.getTags().isEmpty())
                                ? op.getTags().get(0)
                                : "default";
                ops.add(op);
                names.add(desired);
                tags.add(tag);
                nameCounts.merge(desired, 1, Integer::sum);
            }
        }

        // Second pass: apply names, scoping only the ones that collide across tags.
        for (int i = 0; i < ops.size(); i++) {
            String name = names.get(i);
            if (nameCounts.get(name) > 1) {
                String scoped = snakeCase(tags.get(i)) + "_" + snakeCase(name);
                ops.get(i).setOperationId(scoped);
                // Rendered method name inside the class is the short desired name.
                operationIdNameMapping.put(scoped, snakeCase(name));
            } else {
                ops.get(i).setOperationId(name);
            }
        }
    }

    /** Convert camelCase / PascalCase to snake_case (mirrors the former Python {@code _snake_case}). */
    static String snakeCase(String name) {
        String s1 = name.replaceAll("(.)([A-Z][a-z]+)", "$1_$2");
        return s1.replaceAll("([a-z0-9])([A-Z])", "$1_$2").toLowerCase();
    }

    // ------------------------------------------------------------------
    // basePath  ->  servers[0].url
    // ------------------------------------------------------------------

    /**
     * Replaces the spec's servers with a single entry whose URL is the {@code basePath}
     * additional-property, so the generated {@code Configuration} bakes in the service base path.
     */
    private void applyBasePath(OpenAPI openAPI) {
        Object basePath = additionalProperties.get(BASE_PATH_PROPERTY);
        if (basePath instanceof String && !((String) basePath).isEmpty()) {
            openAPI.setServers(
                    new ArrayList<>(
                            Collections.singletonList(new Server().url((String) basePath))));
        }
    }

    // ------------------------------------------------------------------
    // Field(alias=...)  ->  Field(serialization_alias=...)
    // ------------------------------------------------------------------

    /**
     * Rewrites the pydantic field annotation from {@code alias="x"} to
     * {@code serialization_alias="x"} in each property's {@code x-py-typing} string.
     *
     * <p>The alias text is assembled in Java ({@code AbstractPythonCodegen.finalizeType}) and
     * injected into the model template via the {@code x-py-typing} vendor extension, so it cannot
     * be changed in the mustache template alone. Using {@code alias=} makes pydantic take the
     * camelCase wire name as the {@code __init__} parameter, hiding the snake_case field name from
     * type checkers; {@code serialization_alias=} keeps camelCase JSON output while letting the
     * {@code __init__} use the natural snake_case field name. Replaces the former regex post-processing.
     */
    private static void rewriteAliasToSerializationAlias(List<CodegenProperty> vars) {
        if (vars == null) {
            return;
        }
        for (CodegenProperty var : vars) {
            Object typing = var.vendorExtensions.get("x-py-typing");
            if (!(typing instanceof String)) {
                continue;
            }
            String rewritten = replaceAliasKeyword((String) typing);
            if (!rewritten.equals(typing)) {
                var.vendorExtensions.put("x-py-typing", rewritten);
            }
        }
    }

    /**
     * Replace the {@code alias=} keyword argument with {@code serialization_alias=}, matching only
     * the standalone {@code alias} keyword (not {@code validation_alias=} or a substring of another
     * identifier). Mirrors the former Python regex which guarded against a preceding identifier char.
     */
    static String replaceAliasKeyword(String typing) {
        // (?<![\w]) ensures we do not match the tail of e.g. "serialization_alias"/"validation_alias".
        return typing.replaceAll("(?<![\\w])alias=", "serialization_alias=");
    }

    // ------------------------------------------------------------------
    // helpers
    // ------------------------------------------------------------------

    private static String extensionString(Map<String, Object> extensions, String key) {
        if (extensions == null) {
            return null;
        }
        Object value = extensions.get(key);
        return value instanceof String ? (String) value : null;
    }

    @SafeVarargs
    private static <T> T firstNonNull(T... values) {
        for (T value : values) {
            if (value != null) {
                return value;
            }
        }
        return null;
    }
}
