#!/usr/bin/env node
// Structural invariants over the generated data. Unlike the old circular golden
// test, this checks meaningful properties of the output (not "the loader returns
// what's in the file"). It needs only the generated files — no npm deps — so it
// is cheap to run in CI right after the suite.
//
// Checks:
//   1. index.toml and every locale file parse, and the index <-> files agree.
//   2. Section names are valid; day keys are 1..7, month keys 1..12,
//      pattern keys a subset of {full,long,medium,short}.
//   3. No leftover root sentinels (D01..D07 / M01..M12) survive anywhere.
//   4. The default locale ("en") is complete, so the fallback chain always has
//      a value to land on.

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..", "src", "translations");
const LOCALES_DIR = join(ROOT, "locales");
const INDEX_PATH = join(ROOT, "index.toml");
const COMMUNITY_DIR = join(ROOT, "community", "locales");
const COMMUNITY_INDEX = join(ROOT, "community", "index.toml");
const DEFAULT_LOCALE = "en";

const USAGES = ["format", "stand-alone"];
const WIDTHS = ["wide", "abbreviated", "narrow"];
const PATTERN_KEYS = ["full", "long", "medium", "short"];
const SENTINEL = /^(D0[1-7]|M(0[1-9]|1[0-2]))$/;

const errors = [];
const fail = (msg) => errors.push(msg);

// Minimal parser for our generated TOML subset:
//   [section]  /  key = "value"  /  arrays + numbers (top-level, for index)
function parseSections(text) {
  const out = {};
  let cur = null;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    let m = line.match(/^\[(.+)\]$/);
    if (m) {
      cur = m[1];
      out[cur] = out[cur] || {};
      continue;
    }
    m = line.match(/^(\S+)\s*=\s*"((?:[^"\\]|\\.)*)"$/);
    if (m && cur) {
      out[cur][m[1]] = m[2].replace(/\\"/g, '"');
    }
  }
  return out;
}

function parseIndex(text) {
  const locales = [];
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const m = line.match(/^locales\s*=\s*\[(.*)\]$/s);
    if (m) {
      for (const s of m[1].matchAll(/"([^"]+)"/g)) locales.push(s[1]);
    }
  }
  return { locales };
}

// --- load index ---
if (!existsSync(INDEX_PATH)) {
  console.error("FAIL: index.toml not found");
  process.exit(1);
}
const { locales } = parseIndex(readFileSync(INDEX_PATH, "utf8"));
if (locales.length === 0) fail("index.toml lists no locales");

// --- index <-> files agree ---
const filesOnDisk = readdirSync(LOCALES_DIR)
  .filter((f) => f.endsWith(".toml"))
  .map((f) => f.slice(0, -5));
const setIndex = new Set(locales);
const setDisk = new Set(filesOnDisk);
for (const l of locales) {
  if (!setDisk.has(l)) fail(`index lists "${l}" but locales/${l}.toml is missing`);
}
for (const f of filesOnDisk) {
  if (!setIndex.has(f)) fail(`locales/${f}.toml exists but is not in index`);
}

const validSections = new Set(["patterns"]);
for (const c of ["days", "months"]) {
  for (const u of USAGES) for (const w of WIDTHS) validSections.add(`${c}.${u}.${w}`);
}

// Validate section names + key ranges for one parsed file (CLDR or community).
function validateEntries(label, data) {
  for (const [section, entries] of Object.entries(data)) {
    if (!validSections.has(section)) {
      fail(`${label}: unexpected section [${section}]`);
      continue;
    }
    for (const [k, v] of Object.entries(entries)) {
      if (SENTINEL.test(v)) fail(`${label} [${section}] ${k}: leftover sentinel "${v}"`);
      if (section === "patterns") {
        if (!PATTERN_KEYS.includes(k)) fail(`${label} [patterns]: bad key "${k}"`);
      } else if (section.startsWith("days.")) {
        if (!/^[1-7]$/.test(k)) fail(`${label} [${section}]: day key out of range "${k}"`);
      } else if (section.startsWith("months.")) {
        if (!/^(1[0-2]|[1-9])$/.test(k)) fail(`${label} [${section}]: month key out of range "${k}"`);
      }
    }
  }
}

// --- per-file structural checks (CLDR) ---
for (const locale of locales) {
  const p = join(LOCALES_DIR, `${locale}.toml`);
  if (!existsSync(p)) continue; // already reported
  validateEntries(locale, parseSections(readFileSync(p, "utf8")));
}

// --- default locale completeness ---
const defPath = join(LOCALES_DIR, `${DEFAULT_LOCALE}.toml`);
if (!existsSync(defPath)) {
  fail(`default locale "${DEFAULT_LOCALE}" file missing`);
} else {
  const def = parseSections(readFileSync(defPath, "utf8"));
  for (const c of ["days", "months"]) {
    const n = c === "days" ? 7 : 12;
    for (const u of USAGES) {
      for (const w of WIDTHS) {
        const sect = `${c}.${u}.${w}`;
        const entries = def[sect] || {};
        for (let i = 1; i <= n; i++) {
          if (entries[String(i)] === undefined)
            fail(`default locale incomplete: [${sect}] missing key ${i}`);
        }
      }
    }
  }
  for (const k of PATTERN_KEYS) {
    if (!def.patterns || def.patterns[k] === undefined)
      fail(`default locale incomplete: [patterns] missing "${k}"`);
  }
}

// --- community overlay (optional, partial files) ---
let communityCount = 0;
if (existsSync(COMMUNITY_INDEX)) {
  const { locales: comm } = parseIndex(readFileSync(COMMUNITY_INDEX, "utf8"));
  communityCount = comm.length;
  const commSet = new Set(comm);
  const commOnDisk = existsSync(COMMUNITY_DIR)
    ? readdirSync(COMMUNITY_DIR).filter((f) => f.endsWith(".toml")).map((f) => f.slice(0, -5))
    : [];
  for (const l of comm) {
    const p = join(COMMUNITY_DIR, `${l}.toml`);
    if (!existsSync(p)) {
      fail(`community index lists "${l}" but community/locales/${l}.toml is missing`);
      continue;
    }
    // Overlay files are intentionally partial — validate structure only.
    validateEntries(`community/${l}`, parseSections(readFileSync(p, "utf8")));
  }
  for (const f of commOnDisk) {
    if (!commSet.has(f)) fail(`community/locales/${f}.toml exists but is not in community/index.toml`);
  }
}

if (errors.length) {
  console.error(`Invariants FAILED (${errors.length}):`);
  for (const e of errors.slice(0, 50)) console.error("  - " + e);
  if (errors.length > 50) console.error(`  ... and ${errors.length - 50} more`);
  process.exit(1);
}
console.log(`Invariants OK: ${locales.length} locales checked (+${communityCount} community).`);
