# Apktool MCP Server: AI-Powered Android APK Analysis

The **Apktool MCP Server** is a Model Context Protocol (MCP) server designed to expose `Apktool` functionality. It enables AI models, particularly those integrated with the Gemini CLI, to perform advanced Android APK analysis, reverse engineering, and modification workflows.

## 🚀 Key Features

This server bridges the gap between powerful AI capabilities and `Apktool`'s robust set of tools, allowing for automated and intelligent interactions with Android application packages.

* **Decompilation (`decode_apk`):** Decompile APKs into human-readable resources, AndroidManifest.xml, and Smali code for in-depth analysis.
* **Recompilation (`build_apk`):** Recompile modified Smali code and resources back into an installable APK.
* **Framework Management (`install_framework`):** Install necessary framework APKs for decompiling system applications or specific Android versions.
* **Manifest Analysis (`analyze_manifest`, `list_permissions`):** Extract and analyze crucial information from `AndroidManifest.xml`, including declared permissions, activities, services, and receivers.
* **Resource Extraction (`extract_strings`):** Pull string resources for various locales from decompiled APKs.
* **Smali Code Analysis (`find_smali_references`):** Search for specific patterns, API calls, or sensitive information within the Smali assembly code.
* **APK Information (`get_apk_info`):** Obtain basic metadata about an APK file.

## ✨ Integration with Gemini CLI

This server is designed to be consumed by the Gemini CLI. When connected, the Gemini AI can leverage the exposed Apktool functionalities as "tools" and "resources" to facilitate complex APK analysis tasks.

### Exposed Tools (via `list_tools`)

The following `apktool-mcp` tools are available for the AI to call:

* `decode_apk`: Decompile an APK.
* `build_apk`: Recompile an APK.
* `install_framework`: Install a framework APK.
* `analyze_manifest`: Analyze `AndroidManifest.xml`.
* `extract_strings`: Extract string resources.
* `list_permissions`: List all requested permissions.
* `find_smali_references`: Search Smali code.
* `get_apk_info`: Get basic APK information.

### Exposed Resources (via `list_resources` and `read_resource`)

The AI can read specific files from decompiled APKs:

* `apktool://apk/<apk_name>/manifest`: Access the `AndroidManifest.xml` of a decompiled APK.
* `apktool://apk/<apk_name>/apktool_yml`: Access the `apktool.yml` configuration file.

### Available Prompts (via `list_prompts` and `get_prompt`)

Pre-defined prompts guide the AI in common APK analysis scenarios:

* `analyze_security`: Guides the AI to perform a comprehensive security assessment.
* `privacy_audit`: Directs the AI to audit an APK for privacy-related concerns.
* `reverse_engineer_guide`: Provides step-by-step instructions for reverse engineering a target feature within an APK.

## 🛠️ Setup and Running

### Prerequisites

* **Python 3.x:** Ensure you have Python 3 installed.
* **Apktool:** The `apktool` executable must be installed and available in your system's PATH. If not, the server will issue a warning.
    * Installation instructions for Apktool can be found here: [https://ibotpeaches.github.io/Apktool/install/](https://ibotpeaches.github.io/Apktool/install/)
* **MCP Library:** Install the Model Context Protocol library:
    ```bash
    pip install google-mcp
    ```

### Running the Server

1.  **Save the server code:** Save your Python server code (the one you provided) as `apktool_server.py`.
2.  **Run the server:**
    ```bash
    python apktool_server.py
    ```
    The server will run and listen for connections, typically via standard I/O (stdio), which is the default for Gemini CLI integration.

## 🚀 Example Workflow with Gemini CLI (Conceptual)

Once the server is running, you can interact with it using the Gemini CLI.

1.  **Connect the server to Gemini CLI:**
    ```bash
    gemini context add --server-command "python apktool_server.py" apktool-server
    ```
2.  **List available tools/prompts:**
    ```bash
    gemini context list-tools apktool-server
    gemini context list-prompts apktool-server
    ```
3.  **Use a prompt (e.g., to analyze an APK):**
    First, ensure you have an APK file, for example, `my_app.apk`, in a location accessible by the server (e.g., in the same directory or specified with an absolute path).

    ```bash
    gemini prompt apktool-server analyze_security --apk_path my_app.apk
    ```
    The Gemini AI will then use the `apktool-mcp` server to call `decode_apk`, `analyze_manifest`, `list_permissions`, and `find_smali_references` as guided by the prompt, returning its analysis.

4.  **Directly call a tool:**
    ```bash
    gemini tool apktool-server decode_apk --apk_path my_app.apk --output_dir my_app_decompiled
    ```

---