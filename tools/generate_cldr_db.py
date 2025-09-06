import json
import sys
from pathlib import Path

def get_field(data, path, default=None):
    for key in path:
        data = data.get(key, {})
    return data or default

def is_placeholder(val):
    # Placeholder detection for months/days
    return val in [
        "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12",
        "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"
    ] or val.isdigit()

def write_toml_section(f, section, entries, locale):
    keys = list(entries.keys())
    weekday_order = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    # Months: keys are digits
    if all(str(k).isdigit() for k in keys):
        real_count = sum(1 for v in entries.values() if not is_placeholder(v) or locale == "en")
        if real_count == 0:
            return
        print(f"[{section}]", file=f)
        for k in sorted(keys, key=lambda k: int(k)):
            v = entries[k].replace('"', '\\"')
            print(f'{k} = "{v}"', file=f)
        print(file=f)
    # Days: keys are CLDR weekday names
    else:
        real_count = sum(1 for k in weekday_order if k in entries and (not is_placeholder(entries[k]) or locale == "en"))
        if real_count == 0:
            return
        print(f"[{section}]", file=f)
        for idx, wd in enumerate(weekday_order, 1):
            if wd in entries:
                v = entries[wd].replace('"', '\\"')
                print(f'{idx} = "{v}"', file=f)
        print(file=f)

def process_locale(cldr_dir, locale, tomlfile):
    greg_json = Path(cldr_dir) / locale / "ca-gregorian.json"
    if not greg_json.exists():
        return

    with open(greg_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    base = data["main"][locale]["dates"]["calendars"]["gregorian"]

    # Days
    for typ in ["format", "stand-alone"]:
        for width in ["wide", "abbreviated", "narrow"]:
            path = ["days", typ, width]
            days = get_field(base, path)
            if days:
                section = f"{locale}.days.{typ}.{width}"
                write_toml_section(tomlfile, section, days, locale)

    # Months
    for typ in ["format", "stand-alone"]:
        for width in ["wide", "abbreviated", "narrow"]:
            path = ["months", typ, width]
            months = get_field(base, path)
            if months:
                section = f"{locale}.months.{typ}.{width}"
                write_toml_section(tomlfile, section, months, locale)

    # Patterns (date formats)
    date_formats = get_field(base, ["dateFormats"])
    if date_formats:
        keys = ["full", "long", "medium", "short"]
        values = [date_formats.get(key, None) for key in keys]
        if any(values):
            print(f"[{locale}.patterns]", file=tomlfile)
            for key in keys:
                if key in date_formats:
                    val = date_formats[key]
                    if isinstance(val, dict):
                        # CLDR sometimes has {"pattern": ...}
                        val = val.get("pattern", "")
                    val = val.replace('"', '\\"')
                    print(f'{key} = "{val}"', file=tomlfile)
            print(file=tomlfile)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cldr_dates_to_big_toml.py path/to/cldr-dates-full/main/ output.toml")
        sys.exit(1)
    cldr_dir, out_path = sys.argv[1], sys.argv[2]
    locales = sorted([
        p.name for p in Path(cldr_dir).iterdir()
        if p.is_dir() and (p / "ca-gregorian.json").exists()
    ])
    with open(out_path, "w", encoding="utf-8") as tomlfile:
        for locale in locales:
            process_locale(cldr_dir, locale, tomlfile)
    print(f"Wrote {out_path} with {len(locales)} locales")
