import sys
import re

# English months
months_wide = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
months_abbr = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]
mxx = [f"M{str(i).zfill(2)}" for i in range(1, 13)]

def patch_file(toml_path):
    with open(toml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    patched_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check for months.format.wide or months.format.abbreviated section
        match = re.match(
            r"\[(.+)\.months\.format\.(wide|abbreviated)\]", line)
        if match:
            section_type = match.group(2)
            section_lines = [line]
            i += 1
            month_lines = []
            # Collect up to 12 lines for months, skip blank lines after section
            while i < len(lines) and lines[i].strip() and re.match(r'\d+\s*=\s*".*"', lines[i]):
                month_lines.append(lines[i])
                i += 1
            # Check if all 12 lines are M01-M12
            vals = []
            for ml in month_lines:
                m = re.match(r'(\d+)\s*=\s*"(.*)"', ml)
                if m:
                    vals.append(m.group(2).replace('\\"', '"'))
            if vals == mxx:
                # Patch to English names
                src = months_wide if section_type == "wide" else months_abbr
                for idx, name in enumerate(src, 1):
                    v = name.replace('"', '\\"')
                    section_lines.append(f'{idx} = "{v}"\n')
            else:
                section_lines.extend(month_lines)
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
    print(f"Patched months with M01-M12 in {toml_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_months_m01.py path/to/output.toml")
        sys.exit(1)
    patch_file(sys.argv[1])
