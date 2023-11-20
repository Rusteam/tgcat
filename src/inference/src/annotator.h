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
    int AnnotateCategory(const char *text, std::size_t maxChars);

private:
    void PreprocessText(const std::string& text);
private:
    onmt::Tokenizer Tokenizer;

    mutable torch::jit::script::Module LANG;

    bool SaveNotNews = false;
    bool SaveTexts = false;
    bool ComputeNasty = false;
    std::string Mode;
    std::vector<std::vector<std::string>> _listCleanTokensVec;
    std::vector<torch::jit::IValue> _inputsFlow;
    std::string processing_text;
};
