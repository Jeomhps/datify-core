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
