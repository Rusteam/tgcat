#include "tgcat.h"
#include "annotator.h"
#include "document.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char *TGCAT_CATEGORY_NAME[] = {
"Art & Design",
"Bets & Gambling",
"Books",
"Business & Entrepreneurship",
"Cars & Other Vehicles",
"Celebrities & Lifestyle",
"Cryptocurrencies",
"Culture & Events",
"Curious Facts",
"Directories of Channels & Bots",
"Economy & Finance",
"Education",
"Erotic Content",
"Fashion & Beauty",
"Fitness",
"Food & Cooking",
"Foreign Language Learning",
"Health & Medicine",
"History",
"Hobbies & Activities",
"Home & Architecture",
"Humor & Memes",
"Investments",
"Job Listings",
"Kids & Parenting",
"Marketing & PR",
"Motivation & Self-development",
"Movies",
"Music",
"Offers & Promotions",
"Pets",
"Politics & Incidents",
"Psychology & Relationships",
"Real Estate",
"Recreation & Entertainment",
"Religion & Spirituality",
"Science",
"Sports",
"Technology & Internet",
"Travel & Tourism",
"Video Games",
"Other"
};


std::string modelPath("./resources/lid.176.bin");
std::string vocabularyRUPath("./resources/ru_tfidf.txt");
std::string vocabularyENPath("./resources/en_tfidf.txt");
std::string nbRUPath("./resources/ru_tgcat.pt");
std::string nbENPath("./resources/en_tgcat.pt");
size_t maxWords = 10000;
TAnnotator annotator = TAnnotator(modelPath, nbRUPath, nbENPath, maxWords);

int tgcat_init() {
    return 0;
}

int tgcat_detect_language(const struct TelegramChannelInfo *channel_info,
                          char language_code[6]) {
    TDocument document = TDocument();
    document.Text = channel_info->title;
    document.Text.append("\n");
    document.Text.append(channel_info->description);
    document.Text.append("\n");

    for (int i=0;i<channel_info->post_count; i++){
        document.Text.append(channel_info->posts[i]);
        document.Text.append("\n");
    }

    if (!document.Text.empty()) {

        std::optional<TDbDocument> dbDoc = annotator.AnnotateLanguage(document);

        // Return language ISO code if it's not equal to "none"
        std::string none_lg ("none");
        if (dbDoc->Language.compare(none_lg) != 0) {
            memcpy(language_code, dbDoc->Language.c_str(), 3);
            return 0;
        }
    }

    memcpy(language_code, "other", 6);
    return 0;
}

int tgcat_detect_category(const struct TelegramChannelInfo *channel_info,
                          double category_probability[TGCAT_CATEGORY_OTHER + 1]) {
    (void) channel_info;
    memset(category_probability, 0, sizeof(double) * (TGCAT_CATEGORY_OTHER + 1));

    TDocument document = TDocument();
    document.Text = channel_info->title;
    document.Text.append("\n");
    document.Text.append(channel_info->description);
    document.Text.append("\n");

    for (int i=0;i<channel_info->post_count; i++){
        document.Text.append(channel_info->posts[i]);
        document.Text.append("\n");
    }

    if (!document.Text.empty()) {
        at::Dict<std::string, double> categoryProba = annotator.AnnotateCategory(document);
        auto it = categoryProba.begin();
        for (it = categoryProba.begin(); it != categoryProba.end(); it++) {
            for (int i = 0; i < 42; i++) {
                std::string categoryName = it->key();
                if (categoryName == TGCAT_CATEGORY_NAME[i]) {
                    category_probability[i] = it->value();
                }
            }
        }
    }
    return 0;
}
