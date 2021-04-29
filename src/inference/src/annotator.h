#pragma once

#include "config.pb.h"
#include "db_document.h"
#include <torch/script.h>
#include <memory>
#include <optional>
#include <unordered_set>
#include <unordered_map>
#include <vector>

#include <fasttext.h>
#include <onmt/Tokenizer.h>

struct TDocument;


using TFTModelStorage = std::unordered_map<tg::ELanguage, fasttext::FastText>;

class TAnnotator {
public:
    TAnnotator(
            const std::string& modelPath,
            const std::string& nbRUPath,
            const std::string& nbENPath,
            const std::string& nbARPath,
            const std::string& nbFAPath,
            const std::string& nbUZPath,
            size_t maxWords);
    std::optional<TDbDocument> AnnotateLanguage(TDocument& document) const;
    torch::Dict<std::string, double> AnnotateCategory(TDocument& document) const;
    std::vector<std::string> PreprocessText(const std::string& text, const std::string& lang) const;

private:

    std::unordered_set<tg::ELanguage> Languages;

    fasttext::FastText LanguageDetector;

    onmt::Tokenizer Tokenizer;

    mutable torch::jit::script::Module RUNB;
    mutable torch::jit::script::Module ENNB;
    mutable torch::jit::script::Module ARNB;
    mutable torch::jit::script::Module FANB;
    mutable torch::jit::script::Module UZNB;
    size_t maximumWords;

    bool SaveNotNews = false;
    bool SaveTexts = false;
    bool ComputeNasty = false;
    std::string Mode;
};
