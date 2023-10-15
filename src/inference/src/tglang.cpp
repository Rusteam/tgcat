#include "tglang.h"
#include "annotator.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


std::string langPath("./resources/tglang.pt");
size_t maxChars = 1000;

TAnnotator annotator = TAnnotator(langPath, maxChars);


enum TglangLanguage tglang_detect_programming_language(const char *text) {
    int langIdx = annotator.AnnotateCategory(text);
    // Return lang enum
    return TglangLanguage(langIdx);
}
