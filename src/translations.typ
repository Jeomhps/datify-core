#let data = toml("translations/cldr-dates.toml")

#let get-day-name = (
  weekday,
  lang: "en",
  type: "stand-alone",
  width: "wide",
) => {
  if weekday < 1 or weekday > 7 {
    panic("Invalid weekday: " + str(weekday) + " (must be 1–7)")
  }
  if not data.keys().contains(lang) {
    panic("Unknown language: " + lang)
  }
  let days = data.at(lang).at("days")
  if not days.keys().contains(type) {
    panic("Invalid day type: " + type + " (must be 'format' or 'stand-alone')")
  }
  let day_type = days.at(type)
  if not day_type.keys().contains(width) {
    panic("Invalid day width: " + width + " (must be 'wide', 'abbreviated', 'narrow')")
  }
  let width_map = day_type.at(width)
  let weekday_str = str(weekday)
  if not width_map.keys().contains(weekday_str) {
    panic(
      "No day name for weekday " + str(weekday) +
      " in language " + lang +
      ", type " + type +
      ", width " + width
    )
  }
  width_map.at(weekday_str)
}

#let get-month-name = (
  month,
  lang: "en",
  type: "stand-alone", // "format" or "stand-alone"
  width: "wide", // "wide", "abbreviated", "narrow"
) => {
  if month < 1 or month > 12 {
    panic("Invalid month: " + str(month) + " (must be 1–12)")
  }
  if not data.keys().contains(lang) {
    panic("Unknown language: " + lang)
  }
  let months = data.at(lang).at("months")
  if not months.keys().contains(type) {
    panic("Invalid month type: " + type + " (must be 'format' or 'stand-alone')")
  }
  let month_type = months.at(type)
  if not month_type.keys().contains(width) {
    panic("Invalid month width: " + width + " (must be 'wide', 'abbreviated', 'narrow')")
  }
  let width_map = month_type.at(width)
  let month_str = str(month)
  if not width_map.keys().contains(month_str) {
    panic(
      "No month name for month " + str(month) +
      " in language " + lang +
      ", type " + type +
      ", width " + width
    )
  }
  width_map.at(month_str)
}

#let get-date-pattern = (
  pattern_type,
  lang: "en",
) => {
  if not data.keys().contains(lang) {
    panic("Unknown language: " + lang)
  }
  let patterns = data.at(lang).at("patterns")
  if not patterns.keys().contains(pattern_type) {
    panic(
      "Invalid pattern type: " + pattern_type +
      " (must be 'full', 'long', 'medium', 'short')"
    )
  }
  patterns.at(pattern_type)
}
