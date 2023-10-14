#pragma once

#include "config.pb.h"
#include <torch/script.h>
#include <memory>
#include <optional>
#include <unordered_set>
#include <unordered_map>
#include <vector>

#include <fasttext.h>
#include <onmt/Tokenizer.h>


using TFTModelStorage = std::unordered_map<tg::ELanguage, fasttext::FastText>;

class TAnnotator {
public:
    TAnnotator(
            const std::string& langPath,
            size_t maxChars);
    std::vector<double> AnnotateCategory(const char *text) const;
    std::vector<std::string> PreprocessText(const std::string& text) const;

private:
    onmt::Tokenizer Tokenizer;

    mutable torch::jit::script::Module LANG;

    bool SaveNotNews = false;
    bool SaveTexts = false;
    bool ComputeNasty = false;
    std::string Mode;
};
