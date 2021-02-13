#pragma once

#include "config.pb.h"
#include "db_document.h"
#include "embedders/embedder.h"
#include "embedders/tfidf_embedder.h"

#include <memory>
#include <optional>
#include <unordered_set>
#include <unordered_map>
#include <vector>

#include <fasttext.h>
#include <onmt/Tokenizer.h>

struct TDocument;

namespace tinyxml2 {
    class XMLDocument;
}

using TFTModelStorage = std::unordered_map<tg::ELanguage, fasttext::FastText>;

class TAnnotator {
public:
    TAnnotator(
            const std::string& modelPath,
            const std::string& vocabularyRUPath,
            const std::string& vocabularyENPath,
            const std::string& nbRUPath,
            const std::string& nbENPath,
            size_t maxWords);
    std::optional<TDbDocument> AnnotateLanguage(TDocument& document) const;
    at::Dict<std::string, double> AnnotateCategory(TDocument& document) const;
    std::vector<std::string> PreprocessText(const std::string& text, bool isRU) const;

private:
    tg::TAnnotatorConfig Config;

    std::unordered_set<tg::ELanguage> Languages;

    fasttext::FastText LanguageDetector;

    onmt::Tokenizer Tokenizer;

    TTfIdfEmbedder RUEmbedder;
    TTfIdfEmbedder ENEmbedder;

    mutable torch::jit::script::Module RUNB;
    mutable torch::jit::script::Module ENNB;

    bool SaveNotNews = false;
    bool SaveTexts = false;
    bool ComputeNasty = false;
    std::string Mode;
};
