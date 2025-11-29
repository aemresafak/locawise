# Locawise: AI-Powered Localization, Simplified

**Supporting 2 or 3 languages? Support virtually all languages at a coffee price!**

[![PyPI version](https://badge.fury.io/py/locawise.svg)](https://pypi.org/project/locawise/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/locawise.svg)](https://pypi.org/project/locawise/)

Locawise is a smart, context-aware AI localization tool designed to make translating your application's language files effortless and incredibly efficient. It intelligently detects changes in your localization files, automatically translates them using cutting-edge LLMs, and seamlessly integrates into your development workflow.

Stop wrestling with manual translation updates or overpriced services. With Locawise, globalizing your application is no longer a complex chore but a streamlined, automated process.

## What is Locawise?

Locawise is a Python package that revolutionizes your localization workflow. At its core, `locawise`:

1. **Monitors** your specified localization files (e.g., `.json`, `.properties`) for any new or modified translatable strings in your source language.
2. **Leverages powerful AI** (OpenAI & VertexAI models) to provide context-aware translations for these changes into your desired target languages. You can even define project-specific context, terminology, and tone!
3. **Respects your existing translations** and any manual adjustments you've made. It only translates what's new or changed.
4. **Is lightning fast** thanks to asynchronous programming, translating ~2500 keys in under a minute (actual speed may vary based on LLM provider and content).
5. **Is incredibly cost-effective**, especially when using efficient models like Gemini – think pennies for substantial translations.
6. **Maintains a lock file (`i18n.lock`)** for hyper-efficient change detection.
7. **Is resilient**, implementing exponential random backoff to gracefully handle LLM provider rate limits (TPM).

While `locawise` is a powerful Python package callable from the command line, it's also the engine behind the [`locawise-action`](https://github.com/aemresafak/locawise-action), which automates the localization process directly within your GitHub workflows, creating pull requests with the new translations.

## Key Features

* **🤖 AI-Powered Translations:** Harness the power of OpenAI and VertexAI LLMs for accurate, nuanced translations.
* **💡 Context-Aware:** Provide a detailed context, glossary, and even desired tone via a simple YAML configuration to ensure translations fit your brand and application perfectly.
* **⚙️ Flexible Configuration:** A straightforward `i18n.yaml` file lets you define everything from file paths to LLM models.
* **🖥️ CLI Tool:** Easy to use directly from your terminal.
* **⚡ Blazing Fast:** Asynchronous architecture ensures rapid processing of your localization files.
* **💰 Cost-Efficient:** Control your expenses by choosing your LLM provider and model.
* **🔄 Change Detection:** Smartly identifies only new or modified keys for translation using a lock file (`i18n.lock`).
* **🤝 Respects Manual Edits:** Your carefully crafted manual translations in target languages are preserved.
* **💪 Resilient:** Built-in retry mechanisms with exponential backoff to handle API rate limits.
* **📁 Format Support:** Currently supports `.json` and `.properties` files, with an architecture designed for easy expansion to other formats.
* **🔌 Extensible:** Choose your preferred LLM model and provider.

## Why Locawise?

Traditional localization can be a bottleneck:
* **Time-consuming:** Manually tracking changes and translating them across multiple languages is tedious.
* **Expensive:** Outsourcing translations can be costly, especially for frequent updates.
* **Error-prone:** Manual processes increase the risk of inconsistencies and errors.
* **Slows down development:** Localization often becomes an afterthought or a hurdle before release.

Locawise tackles these challenges head-on by providing an automated, intelligent, and developer-friendly solution. Go global faster, smarter, and more affordably!

## Quick Start

Get up and running with `locawise` in a few simple steps.

### 1. Installation

```bash
pip install locawise
```

### 2. Configuration (i18n.yaml)

Create an `i18n.yaml` file in the root of your project (or a path of your choice). This file tells locawise how to handle your translations.

There are **two ways** to configure your language file locations:

#### Option A: Using File Name Pattern (Recommended for consistent naming)

Use this when your files follow a predictable naming pattern:

```yaml
# Localization Configuration
version: v1.0

# Path to the root directory containing your localization files.
# Example: src/main/resources/i18n or ./locales
localization-root-path: "src/main/resources/i18n"

# Pattern for your localization file names.
# Use {language} as a placeholder for the language code (e.g., en, es, fr).
# Use {ext} as a placeholder for the file extension if it's part of the language specific name.
# If your files are like 'en.json', 'fr.json', use "{language}.json"
# If your files are like 'messages_en.properties', 'messages_fr.properties', use "messages_{language}.properties"
# note this will also match messages.properties if source file not found
file-name-pattern: "messages_{language}.properties"

# Source language code (required). This is the language Locawise will translate FROM.
source-lang-code: "en"

# List of target language codes (required). These are the languages Locawise will translate TO.
target-lang-codes:
  - "tr"
  - "ka"
  - "es"
  - "fr"

# (Optional) Provide context for the AI to improve translation quality.
# Describe your application, company, target audience, etc.
context: |
  You work for a fintech company called Serovut. Your job will be to localize their application.
  Serovut offers digital business accounts for SMEs, startups, and freelancers,
  simplifying financial management with services like payments, invoicing, and currency exchange.

# (Optional) Define a glossary of terms to ensure consistent translation.
# Key: Term in the source language
# Value: Definition or preferred translation hint for the AI (the AI will decide the final translation based on context)
glossary:
  merchant: "A business entity using Servouts's services."
  ledger: "A bank account."

# (Optional) Specify the desired tone for the translations (e.g., formal, informal, friendly).
tone: "professional and helpful"

# (Optional) Specify the LLM model to use.
# For OpenAI, e.g., "gpt-4o", "gpt-3.5-turbo".
# For VertexAI, e.g., "gemini-1.5-flash-001", "gemini-1.0-pro".
# If not specified, a default model will be chosen based on the provider.
# llm-model: "gemini-1.5-flash-001"

# (Optional) Specify the LLM location (primarily for VertexAI).
# llm-location: "us-central1"
```

#### Option B: Using Custom Language File Paths (For custom file structures)

Use this when your files have custom names or are located in different subdirectories:

```yaml
# Localization Configuration
version: v1.0

# Path to the root directory containing your localization files.
localization-root-path: "src/main/resources/i18n"

# Source language code (required). This is the language Locawise will translate FROM.
source-lang-code: "en"

# Custom file paths for each language (relative to localization-root-path)
# This approach gives you complete control over file locations and naming
language-file-paths:
  en: "en-US/strings.json"       # Source language
  tr: "tr-TR/strings.json"       # Turkish
  de: "de-DE/strings.json"       # German
  fr: "fr-FR.json"               # French (different structure is fine)
  es: "locales/spanish.json"     # Spanish (in subdirectory)

# (Optional) Context, glossary, tone, and LLM settings work the same
context: |
  Your application context here...

glossary:
  merchant: "A business entity using Servouts's services."

tone: "professional and helpful"
```

**Important**: You must use **either** the pattern-based approach (`file-name-pattern` + `target-lang-codes`) **or** the custom paths approach (`language-file-paths`), but not both.

### 3. Set Up Environment Variables (for LLM Provider Credentials)

`locawise` requires API keys or appropriate authentication for your chosen LLM provider.

**For OpenAI:**
Set the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

**For Vertex AI (Google Cloud):**

1. Ensure you have the Google Cloud CLI installed and configured.
2. Authenticate using `gcloud auth application-default login`.
3. Set the `GOOGLE_CLOUD_PROJECT` environment variable:

```bash
export GOOGLE_CLOUD_PROJECT="your_gcp_project_id"
```

(Alternatively, for non-interactive environments, ensure `GOOGLE_APPLICATION_CREDENTIALS` points to your service account key JSON file.)

### 4. Running Locawise (CLI)

Once installed and configured, you can run locawise from your terminal using Python's module execution flag (`-m`). Point it to your configuration file:

```bash
python3 -m locawise path/to/your/i18n.yaml
```

For example, if your `i18n.yaml` is in the current directory:

```bash
python3 -m locawise i18n.yaml
```

Locawise will then perform the translation process based on your settings.

## Configuration Details (i18n.yaml)

The `i18n.yaml` file is central to using locawise. Here's a breakdown of its fields based on the LocalizationConfig model:

### Required Fields

- **version** (str): The version of the localization configuration schema (e.g., "v1.0").
- **localization-root-path** (str): The path to the directory where your language files are stored (e.g., "locales/", "src/main/resources/i18n"). This is relative to the root of the repository.
- **source-lang-code** (str): The two-letter ISO 639-1 code for your application's primary language (e.g., "en", "es").

### Language File Configuration (Choose ONE approach)

You must provide **either** Option A or Option B:

#### Option A: Pattern-Based Configuration
- **file-name-pattern** (str): A pattern that describes how your localization files are named. Use `{language}` as a placeholder for the language code.
  - Examples:
    - `"{language}.json"` → en.json, fr.json, es.json
    - `"messages_{language}.properties"` → messages_en.properties, messages_fr.properties
- **target-lang-codes** (list[str]): A list of two-letter ISO 639-1 language codes to translate your application into (e.g., ["fr", "de", "ja"]).

**Note**: When using `file-name-pattern`, both fields are required together.

#### Option B: Custom Path Configuration
- **language-file-paths** (dict[str, str]): A dictionary mapping language codes to their specific file paths (relative to `localization-root-path`). Use this when your files don't follow a consistent naming pattern or are in different subdirectories.
  - Example:
    ```yaml
    language-file-paths:
      en: "en-US/strings.json"
      tr: "tr-TR/strings.json"
      de: "german/localization.json"
    ```
  - All language codes (including source language) must be valid two-letter ISO 639-1 codes
  - When using this approach, do not provide `file-name-pattern` or `target-lang-codes`

### Optional Fields

- **context** (str, optional): A multi-line string providing detailed context about your application, its domain, target audience, or any specific style guidelines. This dramatically improves the quality and relevance of AI translations.
- **glossary** (dict[str, str], optional): A dictionary where keys are terms in your source-lang-code and values are their definitions or specific instructions for the AI. This helps maintain consistency for brand-specific or technical terms.
  - Example: `invoice: "A bill for goods or services provided."`
- **tone** (str, optional): Describe the desired tone of voice for the translations (e.g., "formal", "friendly", "playful", "technical").
- **llm-model** (str, optional): Specify a particular LLM model from your chosen provider (e.g., "gpt-4o" for OpenAI, "gemini-1.5-pro-001" for VertexAI). If omitted, locawise will use a sensible default.
- **llm-location** (str, optional): For some providers like VertexAI, you might need to specify the region/location of the LLM model (e.g., "us-central1").

## How It Works

1. **Configuration Load**: When you run `python3 -m locawise <config_file>`, locawise reads your specified YAML configuration.
2. **File Discovery**: It locates your source and target language files using either:
   - The `file-name-pattern` to generate file paths from language codes, or
   - The explicit paths defined in `language-file-paths`
3. **Lock File Check**: It compares the current state of your source language file against the `i18n.lock` file (created in the `localization-root-path`) to identify new or modified keys.
4. **AI Translation**: For each new/modified key, locawise:
   - Constructs a prompt for the LLM, incorporating the key, its source language value, the overall context, relevant glossary entries, and the desired tone.
   - Sends the request to the chosen LLM (OpenAI or VertexAI), selected via config or environment variables.
   - Handles API responses, including rate limits (with exponential backoff for retries).
5. **File Update**: Translations are written to the corresponding target language files. If a target language file doesn't exist, it will be created.
6. **Lock File Update**: The `i18n.lock` file is updated to reflect the newly translated state.

**Important**: locawise is designed to respect any manual changes you make directly to the target language files. It only focuses on translating keys based on changes detected in the source language file relative to the last known state in `i18n.lock`.

## Supported File Formats

Currently, locawise supports:

- `.json` (flat key-value structures and nested objects)
- `.properties` (Java properties files)
- `.xml` (Android strings xml)

The architecture is designed for easy extension. Support for more formats (e.g., YAML, XML, XLIFF, ARB) is planned for the future!

## Choosing Your LLM Provider

You can choose between OpenAI and Google's VertexAI. Ensure credentials and provider choice are correctly set up via environment variables or the `i18n.yaml` config file.

### OpenAI
- **Credentials**: Set the `OPENAI_API_KEY` environment variable.
- **Models**: Specify models like `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo` via `llm-model` in `i18n.yaml`.

### Vertex AI (Google Cloud)
- **Credentials**:
  - Set `GOOGLE_CLOUD_PROJECT` environment variable.
  - Authenticate locally via `gcloud auth application-default login`.
  - For non-interactive/CI environments, use service account keys (e.g., by setting `GOOGLE_APPLICATION_CREDENTIALS`).
- **Models**: Specify models like `gemini-1.5-flash-001`, `gemini-1.0-pro` via `llm-model` and optionally `llm-location` in `i18n.yaml`.

## Using with locawise-action for CI/CD Automation

While locawise is a versatile Python CLI tool, its power truly shines when automated. The [locawise-action](https://github.com/aemresafak/locawise-action) integrates locawise directly into your GitHub workflows.

With just a few lines of YAML in your workflow file, you can:

1. Automatically detect pushes to your main branch.
2. Run locawise (using its CLI interface) to translate new content.
3. Have a Pull Request automatically created with the updated localization files.

Check out the [locawise-action repository](https://github.com/aemresafak/locawise-action) for detailed setup and usage instructions!

## Future Enhancements

We're constantly looking to improve locawise! Here are some things on our radar:

- Support for more file formats (YAML, XLIFF, Android XML, iOS .strings).
- Plausibility checks and validation for translations.
- Auto-context inference.

Have a feature request? Let us know!

## Contributing

We welcome contributions! Whether it's bug reports, feature suggestions, or code contributions, please feel free to open an issue or submit a pull request on our GitHub repository.

## License

locawise is licensed under the [MIT License](LICENSE).
