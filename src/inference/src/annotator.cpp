#include "annotator.h"

#include <string>
#include <locale>
#include <optional>

#include <iostream>
#include <chrono>

TAnnotator::TAnnotator(
            const std::string& langPath):
   // measure loading time
//   auto start_time = std::chrono::high_resolution_clock::now();
//   auto end_time = std::chrono::high_resolution_clock::now();
//    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
   Tokenizer(onmt::Tokenizer::Mode::Conservative)
//    std::cout << "Tokenizer loading time: " << duration.count() << " microseconds" << std::endl;
{

   auto start_time = std::chrono::high_resolution_clock::now();
    LANG = torch::jit::load(langPath);
   auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
    std::cout << "Model loading time: " << duration.count() << " microseconds" << std::endl;
}


std::vector<std::string> TAnnotator::PreprocessText(const std::string& text) const {
    setlocale(LC_ALL, "eng");
    // Tokenize
    std::vector<std::string> tokens;
    Tokenizer.tokenize(text, tokens);
   return tokens;
}

int TAnnotator::AnnotateCategory(const char *text, int maxChars) const {

    auto start_time = std::chrono::high_resolution_clock::now();

    std::string string_text = text;
    std::string cutted_text;
    if (string_text.size() > maxChars){
        cutted_text = string_text.substr(string_text.size() - maxChars, string_text.size());
    }
    else {
        cutted_text = string_text;
    }
    const std::string processing_text = cutted_text;

    auto text_end = std::chrono::high_resolution_clock::now();
    auto text_dur = std::chrono::duration_cast<std::chrono::microseconds>(text_end - start_time);
    std::cout << "Text loading time: " << text_dur.count() << " microseconds" << std::endl;

    // Embedding
    std::vector<std::string> cleanText;
    cleanText = PreprocessText(processing_text);

    auto token_end = std::chrono::high_resolution_clock::now();
    auto token_dur = std::chrono::duration_cast<std::chrono::microseconds>(token_end - text_end);
    std::cout << "Tokenization time: " << token_dur.count() << " microseconds" << std::endl;

    // Prepare input for Naive Bayes
    std::vector<std::vector<std::string>> cleanTextList;
    cleanTextList.push_back(cleanText);

    std::vector<torch::jit::IValue> inputs;
    inputs.emplace_back(cleanTextList);

    // NB predict
    torch::IValue outputTensor;
    outputTensor = LANG.forward(inputs);

    auto nb_end = std::chrono::high_resolution_clock::now();
    auto nb_dur = std::chrono::duration_cast<std::chrono::microseconds>(nb_end - token_end);
    std::cout << "NB time: " << nb_dur.count() << " microseconds" << std::endl;

    auto categoryProba = outputTensor.toList();

    return categoryProba.get(0).toInt();
}
