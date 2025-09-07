#import "/src/translations.typ": *

#for weekday in range(1, 8) {
  get-day-name(weekday, lang: "en", usage: "stand-alone", width: "wide")
  get-day-name(weekday, lang: "en", usage: "stand-alone", width: "abbreviated")
  get-day-name(weekday, lang: "en", usage: "stand-alone", width: "narrow")
  get-day-name(weekday, lang: "en", usage: "format", width: "wide")
  get-day-name(weekday, lang: "en", usage: "format", width: "abbreviated")
  get-day-name(weekday, lang: "en", usage: "format", width: "narrow")
}

#for month in range(1, 13) {
  get-month-name(month, lang: "en", usage: "stand-alone", width: "wide")
  get-month-name(month, lang: "en", usage: "stand-alone", width: "abbreviated")
  get-month-name(month, lang: "en", usage: "stand-alone", width: "narrow")
  get-month-name(month, lang: "en", usage: "format", width: "wide")
  get-month-name(month, lang: "en", usage: "format", width: "abbreviated")
  get-month-name(month, lang: "en", usage: "format", width: "narrow")
}

#get-date-pattern("full", lang: "en")
#get-date-pattern("long", lang: "en")
#get-date-pattern("medium", lang: "en")
#get-date-pattern("short", lang: "en")
#get-date-pattern("yyyy/MM/dd", lang: "en")
