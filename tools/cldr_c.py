import toml

TOML_PATH = "../src/translations/cldr-dates.toml"
C_HEADER_PATH = "../wasm/locales_data.h"
C_SOURCE_PATH = "../wasm/locales_data.c"

DAY_STYLES = [
    "format_wide", "format_abbreviated", "format_narrow",
    "standalone_wide", "standalone_abbreviated", "standalone_narrow"
]
MONTH_STYLES = [
    "format_wide", "format_abbreviated", "format_narrow",
    "standalone_wide", "standalone_abbreviated", "standalone_narrow"
]

def get_items(data, locale, typ, style):
    try:
        parts = style.split("_")
        if parts[0] == "format":
            items = data[locale][typ]["format"][parts[1]]
        else:
            items = data[locale][typ]["stand-alone"][parts[1]]
        rng = range(1, 8) if typ == "days" else range(1, 13)
        return [f'"{items.get(str(i), "")}"' for i in rng]
    except Exception:
        return ['""'] * (7 if typ == "days" else 12)

def get_patterns(data, locale):
    patterns = data[locale].get("patterns", {})
    entries = []
    for key, value in patterns.items():
        entries.append(f'{{"{key}", "{value}"}}')
    entries.append('{NULL, NULL}')
    return entries

data = toml.load(TOML_PATH)
locales = sorted(data.keys())

# Write header
with open(C_HEADER_PATH, "w", encoding="utf-8") as hfile:
    hfile.write(
"""#ifndef LOCALES_DATA_H
#define LOCALES_DATA_H

#define DAYS_IN_WEEK 7
#define MONTHS_IN_YEAR 12

typedef struct {
    const char* key;
    const char* value;
} PatternEntry;

typedef struct {
    const char* locale;
    const char* days_format_wide[DAYS_IN_WEEK];
    const char* days_format_abbreviated[DAYS_IN_WEEK];
    const char* days_format_narrow[DAYS_IN_WEEK];
    const char* days_standalone_wide[DAYS_IN_WEEK];
    const char* days_standalone_abbreviated[DAYS_IN_WEEK];
    const char* days_standalone_narrow[DAYS_IN_WEEK];
    const char* months_format_wide[MONTHS_IN_YEAR];
    const char* months_format_abbreviated[MONTHS_IN_YEAR];
    const char* months_format_narrow[MONTHS_IN_YEAR];
    const char* months_standalone_wide[MONTHS_IN_YEAR];
    const char* months_standalone_abbreviated[MONTHS_IN_YEAR];
    const char* months_standalone_narrow[MONTHS_IN_YEAR];
    const PatternEntry* patterns;
} LocaleData;

extern const LocaleData locales[];
extern const int locales_count;

#endif
""")

# Write source
with open(C_SOURCE_PATH, "w", encoding="utf-8") as cfile:
    cfile.write('#include "locales_data.h"\n\n')

    # Patterns arrays per locale
    for locale in locales:
        pattern_entries = get_patterns(data, locale)
        cfile.write(f'static const PatternEntry patterns_{locale.replace("-", "_")}[] = {{\n')
        for e in pattern_entries:
            cfile.write(f'    {e},\n')
        cfile.write('};\n\n')

    # LocaleData array
    cfile.write('const LocaleData locales[] = {\n')
    for locale in locales:
        entry = [f'"{locale}"']
        # Days
        for style in DAY_STYLES:
            arr = get_items(data, locale, "days", style)
            entry.append("{" + ", ".join(arr) + "}")
        # Months
        for style in MONTH_STYLES:
            arr = get_items(data, locale, "months", style)
            entry.append("{" + ", ".join(arr) + "}")
        # Patterns
        entry.append(f'patterns_{locale.replace("-", "_")}')
        cfile.write(f'    {{{", ".join(entry)}}},\n')
    cfile.write('};\n')
    cfile.write(f'const int locales_count = {len(locales)};\n')
