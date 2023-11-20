#include "tglang.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "annotator.h"

std::string langPath("./resources/tglang.pt");
std::size_t maxChars = 1500;

static TAnnotator annotator = TAnnotator(langPath);

enum TglangLanguage tglang_detect_programming_language(const char *text) {
  int langIdx = annotator.AnnotateCategory(text, maxChars);
  // Return lang enum
  return TglangLanguage(langIdx);
}