#!/usr/bin/env node
// Single-pass CLDR date generator for datify-core.
//
// Replaces the old generate_cldr_db.py + patch_wide_days.py +
// locale_coverage_dashboard.py trio. One pass, one source of truth.
//
// It reads node_modules/cldr-dates-full/main/<locale>/ca-gregorian.json and,
// for every value, compares it against the CLDR root locale (shipped as "und"
// since CLDR v44). A value is "localized" iff it differs from root. Only
// localized values are written (Option A: omit root-equal values); missing
// values are resolved at read time by the Typst loader's fallback chain.
//
// Exception: the DEFAULT locale ("en") is the terminal fallback of that chain,
// so it is written in FULL. Otherwise legitimate English values that happen to
// equal root (e.g. abbreviated days "Mon".."Sun", narrow days "M","T",...)
// would be omitted and the chain would have no value to land on.
//
// Output:
//   src/translations/locales/<locale>.toml   (no locale prefix in sections)
//   src/translations/index.toml              (authoritative locale list + coverage)

import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  readdirSync,
  existsSync,
  rmSync,
} from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO = join(__dirname, "..");
const CLDR_MAIN = join(REPO, "node_modules", "cldr-dates-full", "main");
const ROOT_LOCALE_DIR = "und"; // CLDR root, used only as the comparison baseline
const DEFAULT_LOCALE = "en"; // terminal fallback locale, written in full
const OUT_DIR = join(REPO, "src", "translations", "locales");
const INDEX_PATH = join(REPO, "src", "translations", "index.toml");

const USAGES = ["format", "stand-alone"];
const WIDTHS = ["wide", "abbreviated", "narrow"];
// CLDR weekday keys in ISO order: Monday=1 .. Sunday=7.
const WEEKDAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const MONTH_KEYS = Array.from({ length: 12 }, (_, i) => String(i + 1));
const PATTERN_KEYS = ["full", "long", "medium", "short"];

// Total day+month cells per locale (patterns excluded), for coverage.
const TOTAL_CELLS = USAGES.length * WIDTHS.length * (7 + 12); // 114

function readGregorian(locale) {
  const p = join(CLDR_MAIN, locale, "ca-gregorian.json");
  if (!existsSync(p)) return null;
  const j = JSON.parse(readFileSync(p, "utf8"));
  return j.main[locale].dates.calendars.gregorian;
}

// Normalize a gregorian calendar into:
//   days[usage][width][1..7], months[usage][width]["1".."12"], patterns{key:str}
function extract(greg) {
  const out = { days: {}, months: {}, patterns: {} };
  for (const usage of USAGES) {
    out.days[usage] = {};
    out.months[usage] = {};
    for (const width of WIDTHS) {
      const draw = greg.days?.[usage]?.[width] ?? {};
      const d = {};
      WEEKDAY_ORDER.forEach((wd, i) => {
        if (draw[wd] !== undefined) d[i + 1] = draw[wd];
      });
      out.days[usage][width] = d;

      const mraw = greg.months?.[usage]?.[width] ?? {};
      const m = {};
      for (const k of MONTH_KEYS) {
        if (mraw[k] !== undefined) m[k] = mraw[k];
      }
      out.months[usage][width] = m;
    }
  }
  const df = greg.dateFormats ?? {};
  for (const k of PATTERN_KEYS) {
    let v = df[k];
    if (v === undefined || v === null) continue;
    if (typeof v === "object") v = v.pattern ?? "";
    out.patterns[k] = v;
  }
  return out;
}

// Mirror the old Python escaping: only double quotes are escaped.
function esc(s) {
  return String(s).replace(/"/g, '\\"');
}

// A cell is localized iff it differs from the root value for that cell.
function isLocalized(value, rootValue) {
  return rootValue === undefined || value !== rootValue;
}

// Build the TOML body for one locale. When keepAll is true (default locale),
// every present value is written regardless of root equality.
// Returns { toml, localized } where localized counts day+month cells kept-by-merit.
function buildToml(view, root, keepAll) {
  let out = "";
  let localized = 0;

  const emitNumbered = (category, keysSpec) => {
    for (const usage of USAGES) {
      for (const width of WIDTHS) {
        const cells = view[category][usage][width];
        const rootCells = root[category][usage][width];
        const lines = [];
        for (const k of keysSpec) {
          const v = cells[k];
          if (v === undefined) continue;
          const loc = isLocalized(v, rootCells[k]);
          if (loc) localized++;
          if (keepAll || loc) lines.push(`${k} = "${esc(v)}"`);
        }
        if (lines.length) {
          out += `[${category}.${usage}.${width}]\n` + lines.join("\n") + "\n\n";
        }
      }
    }
  };

  emitNumbered("days", [1, 2, 3, 4, 5, 6, 7]);
  emitNumbered("months", MONTH_KEYS);

  const plines = [];
  for (const k of PATTERN_KEYS) {
    const v = view.patterns[k];
    if (v === undefined) continue;
    if (keepAll || isLocalized(v, root.patterns[k])) {
      plines.push(`${k} = "${esc(v)}"`);
    }
  }
  if (plines.length) {
    out += `[patterns]\n` + plines.join("\n") + "\n\n";
  }

  return { toml: out, localized };
}

function main() {
  if (!existsSync(CLDR_MAIN)) {
    console.error(`Cannot find ${CLDR_MAIN}. Run \`npm ci\` first.`);
    process.exit(1);
  }
  const rootGreg = readGregorian(ROOT_LOCALE_DIR);
  if (!rootGreg) {
    console.error(`Cannot find root locale "${ROOT_LOCALE_DIR}" in ${CLDR_MAIN}.`);
    process.exit(1);
  }
  const root = extract(rootGreg);

  const locales = readdirSync(CLDR_MAIN, { withFileTypes: true })
    .filter(
      (d) =>
        d.isDirectory() &&
        existsSync(join(CLDR_MAIN, d.name, "ca-gregorian.json")),
    )
    .map((d) => d.name)
    .filter((name) => name !== ROOT_LOCALE_DIR) // baseline only, not shipped
    .sort();

  // Regenerate the output directory from scratch so stale files never linger.
  rmSync(OUT_DIR, { recursive: true, force: true });
  mkdirSync(OUT_DIR, { recursive: true });

  const coverage = {};
  for (const locale of locales) {
    const greg = readGregorian(locale);
    const view = extract(greg);
    const keepAll = locale === DEFAULT_LOCALE;
    const { toml, localized } = buildToml(view, root, keepAll);
    writeFileSync(join(OUT_DIR, `${locale}.toml`), toml, "utf8");
    coverage[locale] = ((localized / TOTAL_CELLS) * 100).toFixed(1);
  }

  // index.toml: authoritative locale list + coverage. Locale codes only contain
  // [A-Za-z0-9-], all valid TOML bare keys, so no quoting is needed for keys.
  let idx = "locales = [" + locales.map((l) => `"${l}"`).join(", ") + "]\n\n";
  idx += "[coverage]\n";
  for (const l of locales) {
    idx += `${l} = ${coverage[l]}\n`;
  }
  writeFileSync(INDEX_PATH, idx, "utf8");

  console.log(`Wrote ${locales.length} locale files to ${OUT_DIR}`);
  console.log(`Wrote ${INDEX_PATH}`);
}

main();
