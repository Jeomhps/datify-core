import sys
import re

# English day names, wide and abbreviated, in order
EN_WIDE = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
EN_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

PATCHED = ["D01", "D02", "D03", "D04", "D05", "D06", "D07"]

def patch_file(toml_path):
    with open(toml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    patched_lines = []
    i = 0
    # Track current locale
    current_locale = None

    while i < len(lines):
        line = lines[i]
        # Match locale section
        locale_match = re.match(r"\[([a-zA-Z0-9_-]+)\]", line)
        if locale_match and not ".days." in line:
            current_locale = locale_match.group(1).lower()
        # Only patch if not English
        if current_locale and current_locale.startswith("en"):
            patched_lines.append(line)
            i += 1
            continue

        # Match days section (wide/abbreviated, format or stand-alone)
        days_match = re.match(
            r"\[([a-zA-Z0-9_-]+)\.days\.(format|stand-alone)\.(wide|abbreviated)\]", line
        )
        if days_match:
            section_lines = [line]
            i += 1
            day_lines = []
            # Collect up to 7 lines for days
            while i < len(lines) and lines[i].strip() and re.match(r'\d+\s*=\s*".*"', lines[i]):
                day_lines.append(lines[i])
                i += 1
            # Parse the day values
            days_found = []
            for dl in day_lines:
                m = re.match(r'(\d+)\s*=\s*"(.*)"', dl)
                if m:
                    days_found.append(m.group(2).replace('\\"', '"'))
            # What are we patching?
            kind = days_match.group(3)
            if kind == "wide" and days_found == EN_WIDE:
                # Patch wide if it matches English
                for idx, v in enumerate(PATCHED, 1):
                    section_lines.append(f'{idx} = "{v}"\n')
            elif kind == "abbreviated" and days_found == EN_ABBR:
                # Patch abrv if it matches English
                for idx, v in enumerate(PATCHED, 1):
                    section_lines.append(f'{idx} = "{v}"\n')
            else:
                section_lines.extend(day_lines)
            # Copy rest (blank line after section)
            if i < len(lines) and lines[i].strip() == '':
                section_lines.append('\n')
                i += 1
            patched_lines.extend(section_lines)
        else:
            patched_lines.append(line)
            i += 1

    with open(toml_path, "w", encoding="utf-8") as f:
        f.writelines(patched_lines)
    print(f"Patched days (wide/abbreviated) in {toml_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_days.py path/to/output.toml")
        sys.exit(1)
    patch_file(sys.argv[1])
