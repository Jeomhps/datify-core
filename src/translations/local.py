from babel.dates import get_day_names, get_month_names, get_date_format, Locale
from babel.localedata import locale_identifiers
from pathlib import Path

OUTPUT_TOML_PATH = Path("./data.generated.toml")

def normalize_babel_locale(locale):
    norm = locale.replace("-", "_")
    try:
        Locale.parse(norm)
        return norm
    except:
        pass
    base = norm.split("_")[0]
    try:
        Locale.parse(base)
        return base
    except:
        return None

def kebab_case_locale(babel_locale):
    # Turns en_US -> en-us, zh_Hant_TW -> zh-hant-tw, etc.
    return babel_locale.replace("_", "-").lower()

def get_typst_day_dict(locale, width, context):
    babel_days = get_day_names(width, context=context, locale=locale)
    days = [babel_days.get(i, "") for i in range(7)]  # 0=Mon ... 6=Sun
    return {str(i+1): days[i] for i in range(7)}  # 1=Mon ... 7=Sun

def get_typst_month_dict(locale, width, context):
    babel_months = get_month_names(width, context=context, locale=locale)
    return {str(i): babel_months.get(i, "") for i in range(1, 13)}

def get_babel_patterns(locale):
    pats = {}
    for style in ["full", "long", "medium", "short"]:
        try:
            pats[style] = get_date_format(format=style, locale=locale).pattern
        except Exception:
            pats[style] = ""
    return pats

def write_table(section, d, lines):
    lines.append(f"\n[{section}]\n")
    for k, v in d.items():
        lines.append(f'{k} = "{v}"\n')

def main():
    locales = sorted(locale_identifiers())
    new_toml_lines = []
    for lang in locales:
        babel_locale = normalize_babel_locale(lang)
        if not babel_locale:
            print(f"Skipping unknown locale: {lang}")
            continue
        toml_locale = kebab_case_locale(babel_locale)
        # Days (weekdays)
        for typ in ["format", "stand-alone"]:
            for width in ["wide", "abbreviated", "narrow"]:
                try:
                    day_dict = get_typst_day_dict(babel_locale, width, typ)
                    section = f"{toml_locale}.days.{typ}.{width}"
                    write_table(section, day_dict, new_toml_lines)
                except Exception as e:
                    print(f"Failed days for {lang} {typ} {width}: {e}")
        # Months
        for typ in ["format", "stand-alone"]:
            for width in ["wide", "abbreviated", "narrow"]:
                try:
                    month_dict = get_typst_month_dict(babel_locale, width, typ)
                    section = f"{toml_locale}.months.{typ}.{width}"
                    write_table(section, month_dict, new_toml_lines)
                except Exception as e:
                    print(f"Failed months for {lang} {typ} {width}: {e}")
        # Patterns
        try:
            patterns = get_babel_patterns(babel_locale)
            section = f"{toml_locale}.patterns"
            write_table(section, patterns, new_toml_lines)
        except Exception as e:
            print(f"Failed patterns for {lang}: {e}")

    with open(OUTPUT_TOML_PATH, "w", encoding="utf-8") as f:
        for line in new_toml_lines:
            f.write(line)
    print(f"Wrote Babel-generated TOML to {OUTPUT_TOML_PATH} for {len(locales)} locales.")

if __name__ == "__main__":
    main()
