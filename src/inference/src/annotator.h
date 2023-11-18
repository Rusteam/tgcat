#pragma once

#include <torch/script.h>
#include <memory>
#include <optional>
#include <unordered_set>
#include <unordered_map>
#include <vector>

#include <onmt/Tokenizer.h>


class TAnnotator {
public:
    TAnnotator(
            const std::string& langPath);
    int AnnotateCategory(const char *text, int maxChars) const;
    std::vector<std::string> PreprocessText(const std::string& text) const;

private:
    onmt::Tokenizer Tokenizer;

    mutable torch::jit::script::Module LANG;

    bool SaveNotNews = false;
    bool SaveTexts = false;
    bool ComputeNasty = false;
    std::string Mode;
};
