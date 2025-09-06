import json
import sys
from pathlib import Path

PLACEHOLDER = "<MISSING>"

def get_field(data, path, default=None):
    for key in path:
        data = data.get(key, {})
    return data or default

def is_placeholder(val):
    return val == PLACEHOLDER

def write_toml_section(f, section, keys, entries):
    print(f"[{section}]", file=f)
    for idx, k in enumerate(keys, 1):
        v = entries.get(k, PLACEHOLDER).replace('"', '\\"')
        print(f'{idx} = "{v}"', file=f)
    print(file=f)

def write_months_section(f, section, entries):
    month_keys = [str(i) for i in range(1, 13)]
    print(f"[{section}]", file=f)
    for k in month_keys:
        v = entries.get(k, PLACEHOLDER).replace('"', '\\"')
        print(f'{k} = "{v}"', file=f)
    print(file=f)

def process_locale(cldr_dir, locale, tomlfile):
    greg_json = Path(cldr_dir) / locale / "ca-gregorian.json"
    if not greg_json.exists():
        # Still generate all sections with all placeholders
        base = {}
    else:
        with open(greg_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = data["main"][locale]["dates"]["calendars"]["gregorian"]

    # Days: always output all sections and keys
    day_types = ["format", "stand-alone"]
    widths = ["wide", "abbreviated", "narrow"]
    weekday_order = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
    for typ in day_types:
        for width in widths:
            path = ["days", typ, width]
            days = get_field(base, path, {})
            section = f"{locale}.days.{typ}.{width}"
            write_toml_section(tomlfile, section, weekday_order, days)

    # Months: always output all sections and keys
    month_types = ["format", "stand-alone"]
    widths = ["wide", "abbreviated", "narrow"]
    for typ in month_types:
        for width in widths:
            path = ["months", typ, width]
            months = get_field(base, path, {})
            section = f"{locale}.months.{typ}.{width}"
            write_months_section(tomlfile, section, months)

    # Patterns (date formats): always output all keys
    keys = ["full", "long", "medium", "short"]
    date_formats = get_field(base, ["dateFormats"], {})
    print(f"[{locale}.patterns]", file=tomlfile)
    for key in keys:
        val = date_formats.get(key, PLACEHOLDER)
        if isinstance(val, dict):
            val = val.get("pattern", PLACEHOLDER)
        val = val.replace('"', '\\"')
        print(f'{key} = "{val}"', file=tomlfile)
    print(file=tomlfile)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cldr_dates_to_big_toml_with_placeholders.py path/to/cldr-dates-full/main/ output.toml")
        sys.exit(1)
    cldr_dir, out_path = sys.argv[1], sys.argv[2]
    locales = sorted([
        p.name for p in Path(cldr_dir).iterdir()
        if p.is_dir() and (p / "ca-gregorian.json").exists()
    ])
    # Optionally, get all locales present in CLDR (even if missing ca-gregorian.json)
    # to guarantee structural uniformity:
    # locales = sorted([p.name for p in Path(cldr_dir).iterdir() if p.is_dir()])

    with open(out_path, "w", encoding="utf-8") as tomlfile:
        for locale in locales:
            process_locale(cldr_dir, locale, tomlfile)
    print(f"Wrote {out_path} with {len(locales)} locales")
