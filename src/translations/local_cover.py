import tomli
import re
import sys
from collections import defaultdict

def is_month_placeholder(value):
    if not isinstance(value, str):
        return False
    # Example: M01, M12, etc.
    return bool(re.fullmatch(r'M\d{2}', value.strip()))

def is_day_placeholder(value):
    if not isinstance(value, str):
        return False
    # Example: D01, D07, etc.
    return bool(re.fullmatch(r'D\d{2}', value.strip()))

def is_placeholder(value):
    # Extend with more patterns if used in your TOML
    return is_month_placeholder(value) or is_day_placeholder(value)

def analyze_section(section):
    """Recursively count real vs. total entries, skipping nested dicts only at sub-sub-levels."""
    real, total = 0, 0
    for v in section.values():
        if isinstance(v, dict):
            r, t = analyze_section(v)
            real += r
            total += t
        else:
            total += 1
            if v and not is_placeholder(v):
                real += 1
    return real, total

def main(filename):
    with open(filename, "rb") as f:
        data = tomli.load(f)

    per_lang = defaultdict(lambda: [0, 0])  # lang: [real, total]
    section_coverage = {}

    for section_name, section in data.items():
        if not isinstance(section, dict):
            continue
        real, total = analyze_section(section)
        section_coverage[section_name] = (real, total)
        root_lang = section_name.split('.')[0]
        per_lang[root_lang][0] += real
        per_lang[root_lang][1] += total

    print("Section Coverage:")
    for section, (real, total) in sorted(section_coverage.items()):
        pct = 100.0 * real / total if total else 100.0
        print(f"{section:40}: {real:3d}/{total:3d} ({pct:5.1f}%)")

    print("\nPer Language Coverage:")
    for lang, (real, total) in sorted(per_lang.items()):
        pct = 100.0 * real / total if total else 100.0
        print(f"{lang:10}: {real:4d}/{total:4d} ({pct:5.1f}%)")

    total_real = sum(v[0] for v in per_lang.values())
    total_count = sum(v[1] for v in per_lang.values())
    overall_pct = 100.0 * total_real / total_count if total_count else 100.0
    print(f"\nOverall coverage: {total_real}/{total_count} ({overall_pct:.1f}%)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python local_cover.py path/to/data.generated.toml")
    else:
        main(sys.argv[1])
