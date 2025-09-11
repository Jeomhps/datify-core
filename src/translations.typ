#let p = plugin("../wasm/api.wasm")

#let get-day-name = (weekday, lang: str, usage: str, width: str) => {
  let res = p.get_day_name(
    weekday.to-bytes(), // single byte for C uint8_t
    bytes(lang),
    bytes(usage),
    bytes(width),
  )
  str(res) // decode result as UTF_8 string
}

#let get-month-name = (month, lang: str, usage: str, width: str) => {
  let res = p.get_month_name(
    month.to-bytes(), // single byte for C uint8_t
    bytes(lang),
    bytes(usage),
    bytes(width),
  )
  str(res)
}

#let get-date-pattern = (pattern_type, lang: str) => {
  let res = p.get_date_pattern(
    bytes(pattern_type),
    bytes(lang),
  )
  str(res)
}
