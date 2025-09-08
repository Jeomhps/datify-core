// NOTE TO FUTURE READERS:
//
// The expected panic messages in these tests are written with surrounding double quotes and backslash escapes (e.g. \"text\").
// This is intentional: Typst's `catch` function, as used by the tytanic test runner, returns string panic messages as string literals,
// including the quotes and any necessary escapes. This ensures tests match exactly what Typst produces at runtime.
//
// For example: `panic("foo")` will be caught as the string: panicked with: "foo"
//              (including the quotes)

#import "/src/main.typ": get-day-name, get-month-name, get-date-pattern

// get-day-name: Out-of-range weekday panics (int and str)
#assert-panic(() => get-day-name(0, lang: "en"))
#assert.eq(
  catch(() => get-day-name(0, lang: "en")),
  "panicked with: \"Invalid weekday: 0 (must be 1–7)\""
)
#assert-panic(() => get-day-name("0", lang: "en"))
#assert.eq(
  catch(() => get-day-name("0", lang: "en")),
  "panicked with: \"Invalid weekday: 0 (must be \\\"1\\\"–\\\"7\\\")\""
)
#assert-panic(() => get-day-name(8, lang: "en"))
#assert.eq(
  catch(() => get-day-name(8, lang: "en")),
  "panicked with: \"Invalid weekday: 8 (must be 1–7)\""
)
#assert-panic(() => get-day-name("8", lang: "en"))
#assert.eq(
  catch(() => get-day-name("8", lang: "en")),
  "panicked with: \"Invalid weekday: 8 (must be \\\"1\\\"–\\\"7\\\")\""
)

// get-day-name: Invalid weekday type (e.g. array, auto)
#assert-panic(() => get-day-name((1, 2), lang: "en"))
#assert.eq(
  catch(() => get-day-name((1, 2), lang: "en")),
  "panicked with: \"Invalid weekday type: must be an integer or a string, got array\""
)
#assert-panic(() => get-day-name(auto, lang: "en"))
#assert.eq(
  catch(() => get-day-name(auto, lang: "en")),
  "panicked with: \"Invalid weekday type: must be an integer or a string, got auto\""
)

// get-day-name: Invalid usage
#assert-panic(() => get-day-name(1, lang: "en", usage: "nonsense"))
#assert.eq(
  catch(() => get-day-name(1, lang: "en", usage: "nonsense")),
  "panicked with: \"Invalid day usage: nonsense (must be 'format' or 'stand-alone')\""
)

// get-day-name: Invalid width
#assert-panic(() => get-day-name(1, lang: "en", width: "nonsense"))
#assert.eq(
  catch(() => get-day-name(1, lang: "en", width: "nonsense")),
  "panicked with: \"Invalid day width: nonsense (must be 'wide', 'abbreviated', 'narrow')\""
)

// get-day-name: Invalid language
#assert-panic(() => get-day-name(1, lang: "zz"))
#assert.eq(
  catch(() => get-day-name(1, lang: "zz")),
  "panicked with: \"Unknown language: zz\""
)

// get-day-name: Valid for both int and string (should match)
#assert.eq(get-day-name(1, lang: "en"), get-day-name("1", lang: "en"))

// get-month-name: Out-of-range month panics (int and str)
#assert-panic(() => get-month-name(0, lang: "en"))
#assert.eq(
  catch(() => get-month-name(0, lang: "en")),
  "panicked with: \"Invalid month: 0 (must be 1–12)\""
)
#assert-panic(() => get-month-name("0", lang: "en"))
#assert.eq(
  catch(() => get-month-name("0", lang: "en")),
  "panicked with: \"Invalid month: 0 (must be \\\"1\\\"–\\\"12\\\")\""
)
#assert-panic(() => get-month-name(13, lang: "en"))
#assert.eq(
  catch(() => get-month-name(13, lang: "en")),
  "panicked with: \"Invalid month: 13 (must be 1–12)\""
)
#assert-panic(() => get-month-name("13", lang: "en"))
#assert.eq(
  catch(() => get-month-name("13", lang: "en")),
  "panicked with: \"Invalid month: 13 (must be \\\"1\\\"–\\\"12\\\")\""
)

// get-month-name: Invalid month type (e.g. array, auto)
#assert-panic(() => get-month-name((1, 2), lang: "en"))
#assert.eq(
  catch(() => get-month-name((1, 2), lang: "en")),
  "panicked with: \"Invalid month type: must be an integer or a string, got array\""
)
#assert-panic(() => get-month-name(auto, lang: "en"))
#assert.eq(
  catch(() => get-month-name(auto, lang: "en")),
  "panicked with: \"Invalid month type: must be an integer or a string, got auto\""
)

// get-month-name: Invalid usage
#assert-panic(() => get-month-name(1, lang: "en", usage: "nonsense"))
#assert.eq(
  catch(() => get-month-name(1, lang: "en", usage: "nonsense")),
  "panicked with: \"Invalid month usage: nonsense (must be 'format' or 'stand-alone')\""
)

// get-month-name: Invalid width
#assert-panic(() => get-month-name(1, lang: "en", width: "nonsense"))
#assert.eq(
  catch(() => get-month-name(1, lang: "en", width: "nonsense")),
  "panicked with: \"Invalid month width: nonsense (must be 'wide', 'abbreviated', 'narrow')\""
)

// get-month-name: Invalid language
#assert-panic(() => get-month-name(1, lang: "zz"))
#assert.eq(
  catch(() => get-month-name(1, lang: "zz")),
  "panicked with: \"Unknown language: zz\""
)

// get-month-name: Valid for both int and string (should match)
#assert.eq(get-month-name(1, lang: "en"), get-month-name("1", lang: "en"))

// get-date-pattern: Returns built-in pattern for standard keys, panics otherwise
#assert.eq(get-date-pattern("full", lang: "en"), get-date-pattern("full", lang: "en"))
#assert-panic(() => get-date-pattern("yyyy-MM-dd", lang: "en"))
#assert.eq(
  catch(() => get-date-pattern("yyyy-MM-dd", lang: "en")),
  "panicked with: \"Unknown pattern type: yyyy-MM-dd (must be one of full, long, medium, short)\""
)
#assert-panic(() => get-date-pattern("EEE 'day'", lang: "en"))
#assert.eq(
  catch(() => get-date-pattern("EEE 'day'", lang: "en")),
  "panicked with: \"Unknown pattern type: EEE 'day' (must be one of full, long, medium, short)\""
)

// get-date-pattern: Invalid language
#assert-panic(() => get-date-pattern("short", lang: "zz"))
#assert.eq(
  catch(() => get-date-pattern("short", lang: "zz")),
  "panicked with: \"Unknown language: zz\""
)

// get-date-pattern: Invalid pattern type (e.g. array, auto)
#assert-panic(() => get-date-pattern((1, 2), lang: "en"))
#assert.eq(
  catch(() => get-date-pattern((1, 2), lang: "en")),
  "panicked with: \"Invalid pattern type: must be a string and a known pattern key, got array\""
)
#assert-panic(() => get-date-pattern(auto, lang: "en"))
#assert.eq(
  catch(() => get-date-pattern(auto, lang: "en")),
  "panicked with: \"Invalid pattern type: must be a string and a known pattern key, got auto\""
)
