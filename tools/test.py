import toml
from babel.dates import get_day_names, get_month_names, get_date_format
from pathlib import Path

DATA_TOML_PATH = Path("../src/translations/data.generated.toml")
TYPST_OUT = Path("./test_generated.typ")

def normalize_babel_locale(locale):
    parts = locale.replace('-', '_').split('_')
    if len(parts) == 1:
        return parts[0].lower()
    elif len(parts) == 2:
        if len(parts[1]) == 4:
            return f"{parts[0].lower()}_{parts[1].title()}"
        else:
            return f"{parts[0].lower()}_{parts[1].upper()}"
    elif len(parts) == 3:
        return f"{parts[0].lower()}_{parts[1].title()}_{parts[2].upper()}"
    return locale

def gen_day_name_tests(lang, babel_locale):
    tests = []
    for typ in ["format", "stand-alone"]:
        for width in ["wide", "abbreviated", "narrow"]:
            try:
                babel_days = get_day_names(width, context=typ, locale=babel_locale)
                # Babel: 0 = Monday, ..., 6 = Sunday
                for typst_weekday in range(1, 8):  # 1..7
                    babel_index = (typst_weekday - 1) % 7  # 1=Monday->0, 7=Sunday->6
                    val = babel_days[babel_index]
                    val_escaped = val.replace('"', '\\"')
                    tests.append(
                        f'#assert(get-day-name({typst_weekday}, lang: "{lang}", type: "{typ}", width: "{width}") == "{val_escaped}")'
                    )
            except Exception as e:
                print(f"Skipping get-day-name for {lang} ({typ}, {width}): {e}")
    return tests

def gen_month_name_tests(lang, babel_locale):
    tests = []
    for typ in ["format", "stand-alone"]:
        for width in ["wide", "abbreviated", "narrow"]:
            try:
                babel_months = get_month_names(width, context=typ, locale=babel_locale)
                for month in range(1, 13):
                    val = babel_months.get(month, "")
                    val_escaped = val.replace('"', '\\"')
                    tests.append(
                        f'#assert(get-month-name({month}, lang: "{lang}", type: "{typ}", width: "{width}") == "{val_escaped}")'
                    )
            except Exception as e:
                print(f"Skipping get-month-name for {lang} ({typ}, {width}): {e}")
    return tests

def gen_date_pattern_tests(lang, babel_locale):
    tests = []
    for pat in ["full", "long", "medium", "short"]:
        try:
            babel_pat = get_date_format(format=pat, locale=babel_locale).pattern
            babel_pat_escaped = babel_pat.replace('"', '\\"')
            tests.append(
                f'#assert(get-date-pattern("{pat}", lang: "{lang}") == "{babel_pat_escaped}")'
            )
        except Exception as e:
            print(f"Skipping get-date-pattern for {lang} ({pat}): {e}")
    return tests

def main():
    data = toml.load(DATA_TOML_PATH)
    langs = list(data.keys())
    with open(TYPST_OUT, "w", encoding="utf-8") as f:
        f.write("// Auto-generated tests for data.toml langs\n")
        f.write('#import "../src/translations.typ": get-day-name, get-month-name, get-date-pattern\n\n')
        for lang in langs:
            babel_locale = normalize_babel_locale(lang)
            f.write(f"// Tests for {lang}\n")
            f.writelines([line + "\n" for line in gen_day_name_tests(lang, babel_locale)])
            f.writelines([line + "\n" for line in gen_month_name_tests(lang, babel_locale)])
            f.writelines([line + "\n" for line in gen_date_pattern_tests(lang, babel_locale)])
            f.write("\n")

if __name__ == "__main__":
    main()
