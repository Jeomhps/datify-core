#import "utils.typ": first-letter-to-upper

#let date = toml("translations/data.toml")

#let get-day-name = (
  weekday,
  lang: "en",
  type: "stand-alone",
  width: "wide",
) => {
  // Convert to string for TOML key lookup
  let weekday-str = str(weekday)
  data.at(lang).at("days").at(type).at(width).at(weekday-str)
}

#let get-month-name = (
  month,
  lang: "en",
  type: "stand-alone", // "format" or "stand-alone"
  width: "wide", // "wide", "abbreviated", "narrow"
) => {
  // Convert to string for TOML key lookup (CLDR months are 1-based)
  let month-str = str(month)
  data.at(lang).at("months").at(type).at(width).at(month-str)
}

#let get-date-pattern = (
  pattern_type,
  lang: "en",
) => {
  // pattern_type: "full", "long", "medium", "short"
  data.at(lang).at("patterns").at(pattern_type)
}


// Take a number as an input and a length,
// if number is not as big as length, return the number
// with 0 padding in front, like 9 with length 2
// will return 09
#let pad = (number, length, pad_char: "0") => {
  let str_num = str(number)
  let padding = ""
  while str_num.len() + padding.len() < length {
    padding += pad_char
  }
  return padding + str_num
}

// Take a string and a length, and return the first `length` grapheme clusters
// (what a human sees as characters). If the string is shorter than `length`,
// returns the whole string. This is Unicode-safe and works for non-Latin scripts.
// Example: safe-slice("August", 3) -> "Aug"
// Example: safe-slice("אוגוסט", 3) -> "אוגוס"
#let safe-slice = (s, length) => {
  let clusters = s.clusters()
  let n = if length > clusters.len() { clusters.len() } else { length }
  clusters.slice(0, n).join()
}

#let custom-date-format = (
  date,
  pattern: "full",
  lang: "fr",
) => {
  // Resolve named pattern if needed
  if pattern == "full" or pattern == "long" or pattern == "medium" or pattern == "short" {
    pattern = get-date-pattern(pattern, lang: lang)
  }

  // Symbol lookup
  let symbol-values = (
    "EEEE": get-day-name(date.weekday(), lang: lang, type: "format", width: "wide"),
    "EEE": get-day-name(date.weekday(), lang: lang, type: "format", width: "abbreviated"),
    "MMMM": get-month-name(date.month(), lang: lang, type: "format", width: "wide"),
    "MMM": get-month-name(date.month(), lang: lang, type: "format", width: "abbreviated"),
    "MM": "t",
    "M": str(date.month()),
    "dd": "t",
    "d": str(date.day()),
    "yyyy": str(date.year()),
    "y": str(date.year()),
  )

  // Split pattern on whitespace to get tokens
  let tokens = pattern.split(" ")

  // Build result as a string
  let result = ""
  for i in range(tokens.len()) {
    let token = tokens.at(i)
    let found = false
    // Replace each symbol in token, longest first
    for key in ("EEEE", "MMMM", "yyyy", "EEE", "MMM", "MM", "dd", "M", "d", "y") {
      if not found and token.contains(key) {
        token = token.replace(key, symbol-values.at(key))
        found = true
      }
    }
    // Add space between tokens, but not after the last one
    if i > 0 {
      result += " "
    }
    result += token
  }

  return result
}
