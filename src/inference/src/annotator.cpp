#include "annotator.h"

#include <string>
#include <locale>
#include <optional>

TAnnotator::TAnnotator(
            const std::string& langPath):
   Tokenizer(onmt::Tokenizer::Mode::Conservative)
{
    LANG = torch::jit::load(langPath);
}


std::vector<std::string> TAnnotator::PreprocessText(const std::string& text) const {
    setlocale(LC_ALL, "eng");
    // Tokenize
    std::vector<std::string> tokens;
    Tokenizer.tokenize(text, tokens);
   return tokens;
}

int TAnnotator::AnnotateCategory(const char *text, int maxChars) const {

    std::string string_text = text;
    std::string cutted_text;
    if (string_text.size() > maxChars){
        cutted_text = string_text.substr(string_text.size() - maxChars, string_text.size());
    }
    else {
        cutted_text = string_text;
    }
    const std::string processing_text = cutted_text;

    // Embedding
    std::vector<std::string> cleanText;
    cleanText = PreprocessText(processing_text);

    // Prepare input for Naive Bayes
    std::vector<std::vector<std::string>> cleanTextList;
    cleanTextList.push_back(cleanText);

    std::vector<torch::jit::IValue> inputs;
    inputs.emplace_back(cleanTextList);

    // NB predict
    torch::IValue outputTensor;
    outputTensor = LANG.forward(inputs);

    auto categoryProba = outputTensor.toList();

    return categoryProba.get(0).toInt();
}
