// Curated, human-verified regression fixtures.
//
// Unlike the deleted golden test, these values are NOT derived from the data
// files. They are known-correct values (verified against CLDR / general
// knowledge), so they can actually catch a wrong generator or bad data — not
// merely "the loader returns what's in the file".

#import "/src/main.typ": get-day-name, get-month-name, get-date-pattern

// --- Month names (wide), a spread of scripts ---
#assert.eq(get-month-name(6, lang: "en"), "June")
#assert.eq(get-month-name(6, lang: "fr"), "juin")
#assert.eq(get-month-name(6, lang: "de"), "Juni")
#assert.eq(get-month-name(6, lang: "ja"), "6月")
#assert.eq(get-month-name(6, lang: "ar", usage: "format"), "يونيو")

// --- Day names (wide, format) ---
#assert.eq(get-day-name(1, lang: "de", usage: "format", width: "wide"), "Montag")
#assert.eq(get-day-name(1, lang: "ja", usage: "format", width: "wide"), "月曜日")
#assert.eq(get-day-name(1, lang: "ar", usage: "format", width: "wide"), "الاثنين")

// --- Abbreviated / narrow widths ---
#assert.eq(get-day-name(1, lang: "en", usage: "format", width: "abbreviated"), "Mon")
#assert.eq(get-day-name(1, lang: "en", usage: "format", width: "narrow"), "M")
#assert.eq(get-day-name(1, lang: "fr", usage: "format", width: "abbreviated"), "lun.")
#assert.eq(get-day-name(1, lang: "ja", usage: "format", width: "abbreviated"), "月")

// --- int / str argument parity ---
#assert.eq(get-day-name(1, lang: "en"), get-day-name("1", lang: "en"))
#assert.eq(get-month-name(1, lang: "en"), get-month-name("1", lang: "en"))

// --- Fallback chain ---
// region subtag truncates to the base language
#assert.eq(get-day-name(1, lang: "fr-CA"), get-day-name(1, lang: "fr"))
// multi-subtag truncation
#assert.eq(get-day-name(1, lang: "fr-CA-foobar"), get-day-name(1, lang: "fr"))
// unknown locale falls back to the default ("en")
#assert.eq(get-day-name(1, lang: "zz"), get-day-name(1, lang: "en"))
// a cell omitted because it equals root resolves via the default: French narrow
// Saturday equals root ("S"), so it is omitted from fr.toml and resolves to en.
#assert.eq(get-day-name(6, lang: "fr", usage: "format", width: "narrow"), "S")

// --- Patterns ---
#assert.eq(get-date-pattern("full", lang: "en"), "EEEE, MMMM d, y")
#assert.eq(get-date-pattern("short", lang: "en"), "M/d/yy")

// --- Community overlay (opt-in) ---
// Off by default: pt-BR is community-only, so it resolves to CLDR pt.
#assert.eq(get-day-name(1, lang: "pt-BR", usage: "format", width: "narrow"), "S")
// On: the overlay overrides only the narrow weekdays (Brazilian numbered form).
#assert.eq(get-day-name(1, lang: "pt-BR", usage: "format", width: "narrow", community: true), "2ª")
#assert.eq(get-day-name(1, lang: "pt-BR", usage: "stand-alone", width: "narrow", community: true), "2ª")
// Cells the overlay doesn't define still come from CLDR, even with community:
// true (casing is a presentation choice left to the caller, not baked in).
#assert.eq(get-day-name(1, lang: "pt-BR", usage: "stand-alone", width: "wide", community: true), "segunda-feira")
#assert.eq(get-month-name(11, lang: "pt-BR", usage: "stand-alone", width: "wide", community: true), "novembro")
// Overlay is keyed pt-BR, so plain pt is unaffected even with community: true.
#assert.eq(get-day-name(1, lang: "pt", usage: "format", width: "narrow", community: true), "S")
