#ifndef LOCALES_DATA_H
#define LOCALES_DATA_H

#define DAYS_IN_WEEK 7
#define MONTHS_IN_YEAR 12

typedef struct {
    const char* key;
    const char* value;
} PatternEntry;

typedef struct {
    const char* locale;
    const char* days_format_wide[DAYS_IN_WEEK];
    const char* days_format_abbreviated[DAYS_IN_WEEK];
    const char* days_format_narrow[DAYS_IN_WEEK];
    const char* days_standalone_wide[DAYS_IN_WEEK];
    const char* days_standalone_abbreviated[DAYS_IN_WEEK];
    const char* days_standalone_narrow[DAYS_IN_WEEK];
    const char* months_format_wide[MONTHS_IN_YEAR];
    const char* months_format_abbreviated[MONTHS_IN_YEAR];
    const char* months_format_narrow[MONTHS_IN_YEAR];
    const char* months_standalone_wide[MONTHS_IN_YEAR];
    const char* months_standalone_abbreviated[MONTHS_IN_YEAR];
    const char* months_standalone_narrow[MONTHS_IN_YEAR];
    const PatternEntry* patterns;
} LocaleData;

extern const LocaleData locales[];
extern const int locales_count;

#endif
