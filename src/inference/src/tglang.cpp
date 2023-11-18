#include "tglang.h"
#include "annotator.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


std::string langPath("./resources/tglang.pt");
int maxChars = 1500;

TAnnotator annotator = TAnnotator(langPath);


enum TglangLanguage tglang_detect_programming_language(const char *text) {
    int langIdx = annotator.AnnotateCategory(text, maxChars);
    // Return lang enum
    return TglangLanguage(langIdx);
}
