# datify-core

**Datify-core** is an API library that provides foundational localization data and patterns to format dates, powered directly by Unicode CLDR data ([cldr-json](https://github.com/unicode-org/cldr-json)) and designed for Typst. It is the backend for [Datify](https://github.com/Jeomhps/datify), but is reusable in any Typst project needing localized month and day names or locale-specific date patterns.

If you need high-quality, up-to-date, and standards-based date strings for any supported language, whether for a date formatting tool, localization system, or any Typst workflow, **datify-core** is your solution.

> **Data quality**:
> All locale data is sourced from [cldr-json](https://github.com/unicode-org/cldr-json), which only includes CLDR data that has achieved `draft="contributed"` or `draft="approved"` status. This is the same threshold used by ICU (International Components for Unicode), ensuring high reliability and coverage.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [API Reference](#api-reference)
  - [get-day-name](#get-day-name)
  - [get-month-name](#get-month-name)
  - [get-date-pattern](#get-date-pattern)
- [Supported Locales](#supported-locales)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

---

## Features

- **Full CLDR Coverage:** Hundreds of languages and regional variants for months, weekdays, and patterns.
- **Simple API:** Lookup day/month names and date patterns by locale, usage, and width.
- **Extensible & Updatable:** Data auto-synced from [cldr-json](https://github.com/unicode-org/cldr-json) and can be extended or improved with community contributions.
- **Reusable:** Designed for Datify, but works in any Typst project.

---

## Installation

Install with Typst’s package manager or from preview:

```typst
#import "@preview/datify-core:2.0.0": *
```
(Replace version as needed.)

---

## API Reference

### `get-day-name`

Get the localized name of a weekday.

**Parameters:**

| Name    | Type     | Description                                                          | Default         |
|---------|----------|----------------------------------------------------------------------|-----------------|
| weekday | int/str  | The weekday (1–7, or "1"-"7")                                        | required        |
| lang    | str      | Locale code, e.g. "en", "fr"                                         | "en"            |
| usage   | str      | "stand-alone" (calendar headers) or "format" (full date formatting)  | "stand-alone"   |
| width   | str      | "wide", "abbreviated", "narrow"                                      | "wide"          |

**Example:**
```typst
#get-day-name(1, lang: "fr", usage: "stand-alone", width: "wide") // lundi
#get-day-name(7, lang: "en", usage: "format", width: "abbreviated") // Sun
```

---

### `get-month-name`

Get the localized name of a month.

**Parameters:**

| Name  | Type     | Description                                                                 | Default         |
|-------|----------|-----------------------------------------------------------------------------|-----------------|
| month | int/str  | The month (1–12, or "1"-"12")                                               | required        |
| lang  | str      | Locale code, e.g. "en", "fr"                                                | "en"            |
| usage | str      | "stand-alone" (calendar headers) or "format" (full date formatting)         | "stand-alone"   |
| width | str      | "wide", "abbreviated", "narrow"                                             | "wide"          |

**Example:**
```typst
#get-month-name(2, lang: "en", usage: "format", width: "abbreviated") // Feb
#get-month-name(8, lang: "de", usage: "stand-alone", width: "wide") // August
```

---

### `get-date-pattern`

Get the date formatting pattern for a given locale.

**Parameters:**

| Name         | Type   | Description                                                     | Default |
|--------------|--------|-----------------------------------------------------------------|---------|
| pattern-type | str    | "full", "long", "medium", "short"                               | required|
| lang         | str    | Locale code, e.g. "en", "fr"                                    | "en"    |

**Example:**
```typst
#get-date-pattern("medium", lang: "de") // dd.MM.y
```

---

## Supported Locales

datify-core ships CLDR data for 765 locales — day names, month names, and date
patterns. Each locale stores only the values that are genuinely localized; any
value a locale does not define is resolved through the CLDR fallback chain to its
parent locale and ultimately to the default locale (`en`), so every supported
locale returns sensible output. The full list is in
[`src/translations/index.toml`](src/translations/index.toml).

---

## Testing

To run the full test suite locally, you have two options:

1. **Manual (recommended for contributors)**
    - Install Python (for generating golden test cases)
    - Install [tt (tytanic)](https://github.com/taiki-e/tytanic) to run the Typst tests

    ```sh
    # Generate golden tests
    cd tools
    python generate_golden_test.py
    cd ..
    # Run tests
    tt run
    ```

2. **Via GitHub Actions workflow locally**
    - Install [act](https://github.com/nektos/act)
    - Run the CI workflow as it appears in `.github/workflows/test.yml`:

    ```sh
    act --artifact-server-path /tmp/artifact
    ```

---

## Contributing

- **Native speakers wanted!** If you are fluent in a language and notice missing or incorrect translations, please contribute improvements directly to the TOML files. Community-supplied corrections and completions are very welcome and will be preserved even if CLDR data updates.
- Pull requests for bug fixes, locale improvements, or API enhancements are also welcome.
- See [cldr-json](https://github.com/unicode-org/cldr-json) for upstream data and structure.
- If you wish to run tests, see the [Testing](#testing) section above for setup.

---

## License

MIT © 2025 Jeomhps
CLDR data © Unicode, Inc., used under the [Unicode License](https://unicode.org/copyright.html).

---

## Credits

- [Unicode CLDR Project](https://cldr.unicode.org/)
- [cldr-json](https://github.com/unicode-org/cldr-json)
- [tytanic](https://github.com/taiki-e/tytanic) (Typst test runner)
