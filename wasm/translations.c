#include "emscripten.h"
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "locales_data.h"

#define PROTOCOL_FUNCTION __attribute__((import_module("typst_env")))

PROTOCOL_FUNCTION void wasm_minimal_protocol_send_result_to_host(const uint8_t *ptr, size_t len);
PROTOCOL_FUNCTION void wasm_minimal_protocol_write_args_to_buffer(uint8_t *ptr);

// Locale lookup
static const LocaleData* find_locale(const char* locale) {
    for (int i = 0; i < locales_count; ++i)
        if (strcmp(locales[i].locale, locale) == 0)
            return &locales[i];
    return NULL;
}

static const char *const *select_days_array(const LocaleData* loc, const char* usage, const char* width) {
    if (strcmp(usage, "format") == 0) {
        if (strcmp(width, "wide") == 0) return loc->days_format_wide;
        if (strcmp(width, "abbreviated") == 0) return loc->days_format_abbreviated;
        if (strcmp(width, "narrow") == 0) return loc->days_format_narrow;
    }
    if (strcmp(usage, "stand-alone") == 0) {
        if (strcmp(width, "wide") == 0) return loc->days_standalone_wide;
        if (strcmp(width, "abbreviated") == 0) return loc->days_standalone_abbreviated;
        if (strcmp(width, "narrow") == 0) return loc->days_standalone_narrow;
    }
    return NULL;
}

static const char *const *select_months_array(const LocaleData* loc, const char* usage, const char* width) {
    if (strcmp(usage, "format") == 0) {
        if (strcmp(width, "wide") == 0) return loc->months_format_wide;
        if (strcmp(width, "abbreviated") == 0) return loc->months_format_abbreviated;
        if (strcmp(width, "narrow") == 0) return loc->months_format_narrow;
    }
    if (strcmp(usage, "stand-alone") == 0) {
        if (strcmp(width, "wide") == 0) return loc->months_standalone_wide;
        if (strcmp(width, "abbreviated") == 0) return loc->months_standalone_abbreviated;
        if (strcmp(width, "narrow") == 0) return loc->months_standalone_narrow;
    }
    return NULL;
}

static const PatternEntry* find_pattern(const PatternEntry* entries, const char* key) {
    for (int i = 0; entries[i].key != NULL; ++i)
        if (strcmp(entries[i].key, key) == 0)
            return &entries[i];
    return NULL;
}

// ---- get_day_name ----
// args: weekday (4 bytes as int), lang, usage, width
EMSCRIPTEN_KEEPALIVE
int32_t get_day_name(size_t weekday_len, size_t lang_len, size_t usage_len, size_t width_len) {
    size_t total_len = weekday_len + lang_len + usage_len + width_len;
    uint8_t *args = (uint8_t *)malloc(total_len);
    if (!args) return 1;
    wasm_minimal_protocol_write_args_to_buffer(args);

    int weekday = 0;
    memcpy(&weekday, args, sizeof(int));

    char lang[64], usage[32], width[32];
    memcpy(lang, args + weekday_len, lang_len);
    lang[lang_len] = '\0';
    memcpy(usage, args + weekday_len + lang_len, usage_len);
    usage[usage_len] = '\0';
    memcpy(width, args + weekday_len + lang_len + usage_len, width_len);
    width[width_len] = '\0';

    if (weekday < 1 || weekday > 7) {
        const char* msg = "Invalid weekday: must be 1–7";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    const LocaleData* loc = find_locale(lang);
    if (!loc) {
        const char* msg = "Unknown language/locale";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    const char *const *days = select_days_array(loc, usage, width);
    if (!days) {
        const char* msg = "Invalid day usage or width";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    const char* result = days[weekday - 1];
    if (!result || !*result) {
        const char* msg = "No day name for given parameters";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    wasm_minimal_protocol_send_result_to_host((const uint8_t*)result, strlen(result));
    free(args);
    return 0;
}

// ---- get_month_name ----
// args: month (4 bytes as int), lang, usage, width
EMSCRIPTEN_KEEPALIVE
int32_t get_month_name(size_t month_len, size_t lang_len, size_t usage_len, size_t width_len) {
    size_t total_len = month_len + lang_len + usage_len + width_len;
    uint8_t *args = (uint8_t *)malloc(total_len);
    if (!args) return 1;
    wasm_minimal_protocol_write_args_to_buffer(args);

    int month = 0;
    memcpy(&month, args, sizeof(int));

    char lang[64], usage[32], width[32];
    memcpy(lang, args + month_len, lang_len);
    lang[lang_len] = '\0';
    memcpy(usage, args + month_len + lang_len, usage_len);
    usage[usage_len] = '\0';
    memcpy(width, args + month_len + lang_len + usage_len, width_len);
    width[width_len] = '\0';

    if (month < 1 || month > 12) {
        const char* msg = "Invalid month: must be 1–12";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    const LocaleData* loc = find_locale(lang);
    if (!loc) {
        const char* msg = "Unknown language/locale";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    const char *const *months = select_months_array(loc, usage, width);
    if (!months) {
        const char* msg = "Invalid month usage or width";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    const char* result = months[month - 1];
    if (!result || !*result) {
        const char* msg = "No month name for given parameters";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    wasm_minimal_protocol_send_result_to_host((const uint8_t*)result, strlen(result));
    free(args);
    return 0;
}

// ---- get_date_pattern ----
// args: pattern_type (string), lang (string)
EMSCRIPTEN_KEEPALIVE
int32_t get_date_pattern(size_t pattern_type_len, size_t lang_len) {
    size_t total_len = pattern_type_len + lang_len;
    uint8_t *args = (uint8_t *)malloc(total_len);
    if (!args) return 1;
    wasm_minimal_protocol_write_args_to_buffer(args);

    char pattern_type[32], lang[64];
    memcpy(pattern_type, args, pattern_type_len);
    pattern_type[pattern_type_len] = '\0';
    memcpy(lang, args + pattern_type_len, lang_len);
    lang[lang_len] = '\0';

    const LocaleData* loc = find_locale(lang);
    if (!loc) {
        const char* msg = "Unknown language/locale";
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    const PatternEntry* entry = find_pattern(loc->patterns, pattern_type);
    if (!entry) {
        char msg[128];
        snprintf(msg, sizeof(msg), "Unknown pattern type: %s", pattern_type);
        wasm_minimal_protocol_send_result_to_host((const uint8_t*)msg, strlen(msg));
        free(args); return 1;
    }
    wasm_minimal_protocol_send_result_to_host((const uint8_t*)entry->value, strlen(entry->value));
    free(args);
    return 0;
}
