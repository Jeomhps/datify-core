import toml
from pathlib import Path

DATA_TOML_PATH = Path("../src/translations/cldr-dates.toml")
TYPST_OUT = Path("../tests/golden/test.typ")

def gen_day_name_tests(lang, lang_toml):
    tests = []
    for typ in ["format", "stand-alone"]:
        if "days" not in lang_toml or typ not in lang_toml["days"]:
            continue
        for width in ["wide", "abbreviated", "narrow"]:
            if width not in lang_toml["days"][typ]:
                continue
            toml_days = lang_toml["days"][typ][width]
            for typst_weekday in range(1, 8):
                if str(typst_weekday) not in toml_days:
                    continue
                val = toml_days[str(typst_weekday)].replace('"', '\\"')
                tests.append(
                    f'#assert(get-day-name({typst_weekday}, lang: "{lang}", type: "{typ}", width: "{width}") == "{val}")'
                )
    return tests

def gen_month_name_tests(lang, lang_toml):
    tests = []
    for typ in ["format", "stand-alone"]:
        if "months" not in lang_toml or typ not in lang_toml["months"]:
            continue
        for width in ["wide", "abbreviated", "narrow"]:
            if width not in lang_toml["months"][typ]:
                continue
            toml_months = lang_toml["months"][typ][width]
            for month in range(1, 13):
                if str(month) not in toml_months:
                    continue
                val = toml_months[str(month)].replace('"', '\\"')
                tests.append(
                    f'#assert(get-month-name({month}, lang: "{lang}", type: "{typ}", width: "{width}") == "{val}")'
                )
    return tests

def gen_date_pattern_tests(lang, lang_toml):
    tests = []
    if "patterns" not in lang_toml:
        return tests
    toml_patterns = lang_toml["patterns"]
    for pat in ["full", "long", "medium", "short"]:
        if pat not in toml_patterns:
            continue
        val = toml_patterns[pat].replace('"', '\\"')
        tests.append(
            f'#assert(get-date-pattern("{pat}", lang: "{lang}") == "{val}")'
        )
    return tests

def main():
    data = toml.load(DATA_TOML_PATH)
    langs = list(data.keys())
    with open(TYPST_OUT, "w", encoding="utf-8") as f:
        f.write("// Auto-generated tests for data.toml langs (no CLDR JSON)\n")
        f.write('#import "/src/translations.typ": get-day-name, get-month-name, get-date-pattern\n\n')
        for lang in langs:
            lang_toml = data[lang]
            f.write(f"// Tests for {lang}\n")
            f.writelines([line + "\n" for line in gen_day_name_tests(lang, lang_toml)])
            f.writelines([line + "\n" for line in gen_month_name_tests(lang, lang_toml)])
            f.writelines([line + "\n" for line in gen_date_pattern_tests(lang, lang_toml)])
            f.write("\n")

if __name__ == "__main__":
    main()
