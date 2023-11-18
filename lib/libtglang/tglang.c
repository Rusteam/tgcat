#include "tglang.h"

#include <stdlib.h>
#include <string.h>

enum TglangLanguage tglang_detect_programming_language(const char *text) {
  while (text[0] == '\n' || text[0] == ' ') {
    text++;
  }
  if (strstr(text, "def ") != NULL) {
    return TGLANG_LANGUAGE_PYTHON;
  }
  if (strstr(text, "fn ") != NULL) {
    return TGLANG_LANGUAGE_RUST;
  }
  if (strstr(text, "std::") != NULL) {
    return TGLANG_LANGUAGE_CPLUSPLUS;
  }
  if (text[0] == '{' && text[1] == '"' && text[strlen(text) - 1] == '}') {
    return TGLANG_LANGUAGE_JSON;
  }
  if (strstr(text, "<?php") != NULL || (text[0] == '<' && text[1] == '?')) {
    return TGLANG_LANGUAGE_PHP;
  }
  if (strstr(text, "console.log(") != NULL || strstr(text, "document.write") != NULL || strstr(text, "innerHTML") != NULL) {
    return TGLANG_LANGUAGE_JAVASCRIPT;
  }
  if (strstr(text, "<div ") != NULL || strstr(text, "<html") != NULL) {
    return TGLANG_LANGUAGE_HTML;
  }
  if (strstr(text, ":flags.") != NULL) {
    return TGLANG_LANGUAGE_TL;
  }
  return TGLANG_LANGUAGE_OTHER;
}
