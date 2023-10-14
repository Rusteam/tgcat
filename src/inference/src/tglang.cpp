#include "tglang.h"
#include "annotator.h"
#include "document.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


std::string modelPath("./resources/lid.176.bin");
std::string vocabularyENPath("./resources/en_tfidf.txt");
std::string langPath("./resources/tglang.pt");
size_t maxChars = 1000;

TAnnotator annotator = TAnnotator(modelPath, langPath, maxChars);


enum TglangLanguage tglang_detect_programming_language(const char *text) {
    if (!text.empty()) {
        std::vector<double> langProba = annotator.AnnotateCategory(text);

        // Find maximum category index
        int maxIndex = 0;
        double maxProba = 0.0;
        for (int i = 0; i < 100; i++) {
            if (vector[i] >= maxProba) {
                maxProba = vector[i];
                maxIndex = i;
            }
        }
        // Return lang enum
        return TglangLanguage(maxIndex);
    }
    return 0;
}
