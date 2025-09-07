// NOTE TO FUTURE READERS:
//
// The expected panic messages in these tests are written with surrounding double quotes and backslash escapes (e.g. \"text\").
// This is intentional: Typst's `catch` function, as used by the tytanic test runner, returns string panic messages as string literals,
// including the quotes and any necessary escapes. This ensures tests match exactly what Typst produces at runtime.
//
// For example: `panic("foo")` will be caught as the string: panicked with: "foo"
//              (including the quotes)

#import "/src/translations.typ": get-day-name, get-month-name, get-date-pattern

// get-day-name: Out-of-range weekday panics
#assert-panic(() => get-day-name(0, lang: "en"))
#assert.eq(
  catch(() => get-day-name(0, lang: "en")),
  "panicked with: \"Invalid weekday: 0 (must be 1–7)\""
)

#assert-panic(() => get-day-name(8, lang: "en"))
#assert.eq(
  catch(() => get-day-name(8, lang: "en")),
  "panicked with: \"Invalid weekday: 8 (must be 1–7)\""
)

// get-day-name: Invalid type
#assert-panic(() => get-day-name(1, lang: "en", type: "nonsense"))
#assert.eq(
  catch(() => get-day-name(1, lang: "en", type: "nonsense")),
  "panicked with: \"Invalid day type: nonsense (must be 'format' or 'stand-alone')\""
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

// get-month-name: Out-of-range month panics
#assert-panic(() => get-month-name(0, lang: "en"))
#assert.eq(
  catch(() => get-month-name(0, lang: "en")),
  "panicked with: \"Invalid month: 0 (must be 1–12)\""
)

#assert-panic(() => get-month-name(13, lang: "en"))
#assert.eq(
  catch(() => get-month-name(13, lang: "en")),
  "panicked with: \"Invalid month: 13 (must be 1–12)\""
)

// get-month-name: Invalid type
#assert-panic(() => get-month-name(1, lang: "en", type: "nonsense"))
#assert.eq(
  catch(() => get-month-name(1, lang: "en", type: "nonsense")),
  "panicked with: \"Invalid month type: nonsense (must be 'format' or 'stand-alone')\""
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

// get-date-pattern: Invalid pattern type
#assert-panic(() => get-date-pattern("not-a-pattern", lang: "en"))
#assert.eq(
  catch(() => get-date-pattern("not-a-pattern", lang: "en")),
  "panicked with: \"Invalid pattern type: not-a-pattern (must be 'full', 'long', 'medium', 'short')\""
)

// get-date-pattern: Invalid language
#assert-panic(() => get-date-pattern("short", lang: "zz"))
#assert.eq(
  catch(() => get-date-pattern("short", lang: "zz")),
  "panicked with: \"Unknown language: zz\""
)
