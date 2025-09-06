import toml
import json
from pathlib import Path

DATA_TOML_PATH = Path("../src/translations/data.generated.toml")
CLDR_PATH = Path("../cldr-json/cldr-json/cldr-dates-full/main")
TYPST_OUT = Path("../tests/test_generated.typ")

def load_cldr_days(lang, typ, width):
    with open(CLDR_PATH / lang / "ca-gregorian.json", encoding="utf-8") as f:
        data = json.load(f)
    return data["main"][lang]["dates"]["calendars"]["gregorian"]["days"][typ][width]

def load_cldr_months(lang, typ, width):
    with open(CLDR_PATH / lang / "ca-gregorian.json", encoding="utf-8") as f:
        data = json.load(f)
    return data["main"][lang]["dates"]["calendars"]["gregorian"]["months"][typ][width]

def load_cldr_patterns(lang):
    with open(CLDR_PATH / lang / "ca-gregorian.json", encoding="utf-8") as f:
        data = json.load(f)
    return data["main"][lang]["dates"]["calendars"]["gregorian"]["dateFormats"]

def gen_day_name_tests(lang, lang_toml):
    tests = []
    for typ in ["format", "stand-alone"]:
        for width in ["wide", "abbreviated", "narrow"]:
            try:
                cldr_map = load_cldr_days(lang, typ, width)
                toml_days = lang_toml["days"][typ][width]
                # CLDR: keys are "sun", "mon", ...; typst/TOML: 1..7 (1=Monday)
                cldr_keys = list(cldr_map.keys())
                # Make CLDR index 0=Sunday, 1=Monday, etc.
                cldr_weekdays = [cldr_map[k] for k in cldr_keys]
                # Map Typst 1..7 to CLDR (Monday=2nd, Sunday=1st)
                for typst_weekday in range(1, 8):
                    # CLDR order: sun, mon, tue, ... (0=Sunday)
                    cldr_idx = (typst_weekday % 7)
                    val = cldr_weekdays[cldr_idx]
                    val_escaped = val.replace('"', '\\"')
                    expected = toml_days[str(typst_weekday)]
                    tests.append(
                        f'#assert(get-day-name({typst_weekday}, lang: "{lang}", type: "{typ}", width: "{width}") == "{val_escaped}")  // TOML: "{expected}"'
                    )
            except Exception as e:
                print(f"Skipping get-day-name for {lang} ({typ}, {width}): {e}")
    return tests

def gen_month_name_tests(lang, lang_toml):
    tests = []
    for typ in ["format", "stand-alone"]:
        for width in ["wide", "abbreviated", "narrow"]:
            try:
                cldr_map = load_cldr_months(lang, typ, width)
                toml_months = lang_toml["months"][typ][width]
                for month in range(1, 13):
                    val = cldr_map[str(month)]
                    val_escaped = val.replace('"', '\\"')
                    expected = toml_months[str(month)]
                    tests.append(
                        f'#assert(get-month-name({month}, lang: "{lang}", type: "{typ}", width: "{width}") == "{val_escaped}")  // TOML: "{expected}"'
                    )
            except Exception as e:
                print(f"Skipping get-month-name for {lang} ({typ}, {width}): {e}")
    return tests

def gen_date_pattern_tests(lang, lang_toml):
    tests = []
    try:
        cldr_patterns = load_cldr_patterns(lang)
        toml_patterns = lang_toml["patterns"]
        for pat in ["full", "long", "medium", "short"]:
            cldr_pat = cldr_patterns[pat]
            cldr_pat_escaped = cldr_pat.replace('"', '\\"')
            expected = toml_patterns[pat]
            tests.append(
                f'#assert(get-date-pattern("{pat}", lang: "{lang}") == "{cldr_pat_escaped}")  // TOML: "{expected}"'
            )
    except Exception as e:
        print(f"Skipping get-date-pattern for {lang}: {e}")
    return tests

def main():
    data = toml.load(DATA_TOML_PATH)
    langs = list(data.keys())
    with open(TYPST_OUT, "w", encoding="utf-8") as f:
        f.write("// Auto-generated tests for data.toml langs vs CLDR JSON\n")
        f.write('#import "../src/translations.typ": get-day-name, get-month-name, get-date-pattern\n\n')
        for lang in langs:
            if not (CLDR_PATH / lang).exists():
                print(f"CLDR JSON missing for {lang}, skipping")
                continue
            lang_toml = data[lang]
            f.write(f"// Tests for {lang}\n")
            f.writelines([line + "\n" for line in gen_day_name_tests(lang, lang_toml)])
            f.writelines([line + "\n" for line in gen_month_name_tests(lang, lang_toml)])
            f.writelines([line + "\n" for line in gen_date_pattern_tests(lang, lang_toml)])
            f.write("\n")

if __name__ == "__main__":
    main()
