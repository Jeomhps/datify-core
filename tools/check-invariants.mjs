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
//   5. Coverage is present for every locale and within [0, 100].

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..", "src", "translations");
const LOCALES_DIR = join(ROOT, "locales");
const INDEX_PATH = join(ROOT, "index.toml");
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
  const coverage = {};
  let inCoverage = false;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    if (line === "[coverage]") {
      inCoverage = true;
      continue;
    }
    let m = line.match(/^locales\s*=\s*\[(.*)\]$/s);
    if (m) {
      for (const s of m[1].matchAll(/"([^"]+)"/g)) locales.push(s[1]);
      continue;
    }
    if (inCoverage) {
      m = line.match(/^(\S+)\s*=\s*([0-9.]+)$/);
      if (m) coverage[m[1]] = parseFloat(m[2]);
    }
  }
  return { locales, coverage };
}

// --- load index ---
if (!existsSync(INDEX_PATH)) {
  console.error("FAIL: index.toml not found");
  process.exit(1);
}
const { locales, coverage } = parseIndex(readFileSync(INDEX_PATH, "utf8"));
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

// --- per-file structural checks ---
for (const locale of locales) {
  const p = join(LOCALES_DIR, `${locale}.toml`);
  if (!existsSync(p)) continue; // already reported
  const data = parseSections(readFileSync(p, "utf8"));
  for (const [section, entries] of Object.entries(data)) {
    if (!validSections.has(section)) {
      fail(`${locale}: unexpected section [${section}]`);
      continue;
    }
    for (const [k, v] of Object.entries(entries)) {
      if (SENTINEL.test(v)) fail(`${locale} [${section}] ${k}: leftover sentinel "${v}"`);
      if (section === "patterns") {
        if (!PATTERN_KEYS.includes(k)) fail(`${locale} [patterns]: bad key "${k}"`);
      } else if (section.startsWith("days.")) {
        if (!/^[1-7]$/.test(k)) fail(`${locale} [${section}]: day key out of range "${k}"`);
      } else if (section.startsWith("months.")) {
        if (!/^(1[0-2]|[1-9])$/.test(k)) fail(`${locale} [${section}]: month key out of range "${k}"`);
      }
    }
  }
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

// --- coverage present and in range ---
for (const l of locales) {
  const c = coverage[l];
  if (c === undefined) fail(`coverage missing for "${l}"`);
  else if (c < 0 || c > 100) fail(`coverage out of range for "${l}": ${c}`);
}

if (errors.length) {
  console.error(`Invariants FAILED (${errors.length}):`);
  for (const e of errors.slice(0, 50)) console.error("  - " + e);
  if (errors.length > 50) console.error(`  ... and ${errors.length - 50} more`);
  process.exit(1);
}
console.log(`Invariants OK: ${locales.length} locales checked.`);
