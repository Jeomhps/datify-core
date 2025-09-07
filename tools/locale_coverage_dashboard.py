import re

TOML_PATH = "../src/translations/cldr-dates.toml"
README_PATH = "../README.md"
DASHBOARD_START = "<!--locale-dashboard-start-->"
DASHBOARD_END = "<!--locale-dashboard-end-->"

# Patterns to match [locale.days.*] and [locale.months.*] sections and extract section type
SECTION_PATTERNS = [
    r"\[(?P<locale>[^\]]+)\.days\.(format|stand-alone)\.(?P<stype>wide|abbreviated|narrow)\]",
    r"\[(?P<locale>[^\]]+)\.months\.(format|stand-alone)\.(?P<stype>wide|abbreviated|narrow)\]",
]

def get_fake_set(is_day, section_type):
    if is_day:
        # All days sections use D01-D07 as placeholders
        return {"D01", "D02", "D03", "D04", "D05", "D06", "D07"}
    else:
        if section_type == "narrow":
            # For months.narrow and months.stand-alone.narrow: 1-12 are placeholders
            return set(str(i) for i in range(1, 13))
        else:
            # For all other months sections: M01-M12 are placeholders
            return set("M%02d" % i for i in range(1, 13))

def parse_toml_sections():
    with open(TOML_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    locale_stats = {}

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip [locale.patterns] sections entirely
        if ".patterns]" in line:
            i += 1
            continue

        matched_section = None
        section_type = None
        is_day = False
        is_month = False
        for pattern in SECTION_PATTERNS:
            m = re.match(pattern, line)
            if m:
                matched_section = m
                section_type = m.group("stype")
                is_day = ".days." in line
                is_month = ".months." in line
                break
        if not matched_section:
            i += 1
            continue

        locale = matched_section.group("locale")
        expect = 7 if is_day else 12
        fake_set = get_fake_set(is_day, section_type)

        values = []
        i += 1
        while i < len(lines) and re.match(r'\d+\s*=\s*".*"', lines[i].strip()):
            val = re.match(r'\d+\s*=\s*"(.*)"', lines[i].strip()).group(1)
            values.append(val)
            i += 1

        if locale not in locale_stats:
            locale_stats[locale] = {"localized": 0, "total": 0}
        localized = sum(1 for v in values if v not in fake_set)
        locale_stats[locale]["localized"] += localized
        locale_stats[locale]["total"] += expect

    return locale_stats

def make_color(pct):
    if pct >= 99.5:
        return "🟩"
    elif pct >= 80:
        return "🟨"
    elif pct >= 40:
        return "🟧"
    else:
        return "🟥"

def make_dashboard_md(locale_stats):
    rows = []
    for locale in sorted(locale_stats.keys()):
        stat = locale_stats[locale]
        pct = 100 * stat["localized"] / stat["total"] if stat["total"] else 0
        color = make_color(pct)
        rows.append(f"| `{locale}` | {color} {pct:.1f}% | {stat['localized']}/{stat['total']} |")
    md = (
        "| Locale | Coverage | Localized/Total |\n"
        "|--------|----------|-----------------|\n"
        + "\n".join(rows)
    )
    return md

def update_readme(dashboard_md):
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
    start = content.find(DASHBOARD_START)
    end = content.find(DASHBOARD_END)
    if start == -1 or end == -1:
        print("Insert the following markers in your README:")
        print(DASHBOARD_START)
        print(DASHBOARD_END)
        print("Here is the dashboard markdown:\n")
        print(dashboard_md)
        return
    new_content = (
        content[:start+len(DASHBOARD_START)] + "\n\n"
        + dashboard_md + "\n\n"
        + content[end:]
    )
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    stats = parse_toml_sections()
    dashboard_md = make_dashboard_md(stats)
    print(dashboard_md)
    update_readme(dashboard_md)
