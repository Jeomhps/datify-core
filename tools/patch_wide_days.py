import sys
import re

EN_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
EN_WIDE = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
EN_NARROW = ["M", "T", "W", "T", "F", "S", "S"]
PATCHED = ["D01", "D02", "D03", "D04", "D05", "D06", "D07"]

def patch_file(toml_path):
    with open(toml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    patched_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        # Match days section (wide/abbreviated/narrow, format or stand-alone)
        days_match = re.match(
            r"\[([a-zA-Z0-9_-]+)\.days\.(format|stand-alone)\.(wide|abbreviated|narrow)\]", line
        )
        if days_match:
            locale_code = days_match.group(1)
            if locale_code.lower().startswith("en"):
                patched_lines.append(line)
                i += 1
                # Copy lines for this section as is (day lines + blank line)
                while i < len(lines) and (lines[i].strip() and re.match(r'\d+\s*=\s*".*"', lines[i])):
                    patched_lines.append(lines[i])
                    i += 1
                if i < len(lines) and lines[i].strip() == '':
                    patched_lines.append('\n')
                    i += 1
                continue

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
            kind = days_match.group(3)
            if kind == "wide" and days_found == EN_WIDE:
                for idx, v in enumerate(PATCHED, 1):
                    section_lines.append(f'{idx} = "{v}"\n')
            elif kind == "abbreviated" and days_found == EN_ABBR:
                for idx, v in enumerate(PATCHED, 1):
                    section_lines.append(f'{idx} = "{v}"\n')
            elif kind == "narrow" and days_found == EN_NARROW:
                for idx, v in enumerate(PATCHED, 1):
                    section_lines.append(f'{idx} = "{v}"\n')
            else:
                section_lines.extend(day_lines)
            # Copy blank line after section
            if i < len(lines) and lines[i].strip() == '':
                section_lines.append('\n')
                i += 1
            patched_lines.extend(section_lines)
        else:
            patched_lines.append(line)
            i += 1

    with open(toml_path, "w", encoding="utf-8") as f:
        f.writelines(patched_lines)
    print(f"Patched days (wide/abbreviated/narrow) in {toml_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_days.py path/to/output.toml")
        sys.exit(1)
    patch_file(sys.argv[1])
