#include "tglang.h"
#include "annotator.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


std::string langPath("./resources/tglang.pt");
size_t maxChars = 1000;

TAnnotator annotator = TAnnotator(langPath, maxChars);


enum TglangLanguage tglang_detect_programming_language(const char *text) {
    std::vector<double> langProba = annotator.AnnotateCategory(text);

    // Find maximum category index
    int maxIndex = 0;
    double maxProba = 0.0;
    for (int i = 0; i < 100; i++) {
        if (langProba[i] >= maxProba) {
            maxProba = langProba[i];
            maxIndex = i;
        }
    }
    // Return lang enum
    return TglangLanguage(maxIndex);
}
