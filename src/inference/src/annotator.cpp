#include "annotator.h"
#include "thread_pool.h"
#include "timer.h"
#include <boost/algorithm/string/join.hpp>
#include <boost/locale.hpp>

#include <string>
#include <locale>
#include <regex>
#include <optional>
#include <boost/algorithm/string.hpp>
#include "boost/regex.hpp"
#include "boost/algorithm/string/regex.hpp"

TAnnotator::TAnnotator(
            const std::string& langPath):
        Tokenizer(onmt::Tokenizer::Mode::Conservative)
{
    LANG = torch::jit::load(langPath);
}


std::vector<std::string> TAnnotator::PreprocessText(const std::string& text) const {
    setlocale(LC_ALL, "rus");
    // Remove links
    //std::regex urlRe("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+");
    //std::string processed_text = std::regex_replace(text, urlRe, " ");

    // Tokenize
    std::vector<std::string> tokens;
    Tokenizer.tokenize(text, tokens);

    // Leave only words
    /*
    std::vector<std::string> clean_tokens;
    boost::regex xRegEx;
    xRegEx = boost::regex("[a-z]+");

    for (int i = 0; i <= tokens.size() - 1; i++) {
        boost::smatch xResults;
        if(boost::regex_match(tokens[i],xResults, xRegEx)){
            if (tokens[i].size() > 1){
                clean_tokens.push_back(tokens[i]);
            }
        }
    }
    */
    //std::string clean_token_string = boost::join(clean_tokens, " ");
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
