import sys
import re

# Mapping from abbreviation to wide form
abbr_to_wide = {
    "Mon": "Monday",
    "Tue": "Tuesday",
    "Wed": "Wednesday",
    "Thu": "Thursday",
    "Fri": "Friday",
    "Sat": "Saturday",
    "Sun": "Sunday",
}

weekday_order = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
abbrs = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
wide = ["D01", "DO2", "D03", "D04", "D05", "D06", "D07"]

def patch_file(toml_path):
    with open(toml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    patched_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"\[(.+)\.days\.(format|stand-alone)\.wide\]", line)
        if match:
            # Found a wide days section
            section_start = i
            section_lines = [line]
            i += 1
            day_lines = []
            # Collect up to 7 lines for days, skip blank lines after section
            while i < len(lines) and lines[i].strip() and re.match(r'\d+\s*=\s*".*"', lines[i]):
                day_lines.append(lines[i])
                i += 1
            # Check if all 7 lines exist and are Mon-Tue-Wed...
            days_found = []
            for dl in day_lines:
                m = re.match(r'(\d+)\s*=\s*"(.*)"', dl)
                if m:
                    days_found.append(m.group(2).replace('\\"', '"'))
            if days_found == abbrs:
                # Patch to wide names, preserving numbering
                for idx, w in enumerate(wide, 1):
                    v = w.replace('"', '\\"')
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
    print(f"Patched wide day names in {toml_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_wide_days.py path/to/output.toml")
        sys.exit(1)
    patch_file(sys.argv[1])
