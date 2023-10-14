#include "annotator.h"
#include "thread_pool.h"
#include "timer.h"
#include "util.h"
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
            const std::string& langPath,
        size_t maxChars):
        Tokenizer(onmt::Tokenizer::Mode::Conservative, onmt::Tokenizer::Flags::CaseFeature)
{
    LANG = torch::jit::load(langPath);
}


std::vector<std::string> TAnnotator::PreprocessText(const std::string& text) const {
    setlocale(LC_ALL, "rus");
    // Remove links
    std::regex urlRe("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+");
    std::string processed_text = std::regex_replace(text, urlRe, " ");

    // Tokenize
    std::vector<std::string> tokens;
    Tokenizer.tokenize(processed_text, tokens);

    // Leave only words
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
    //std::string clean_token_string = boost::join(clean_tokens, " ");
    return clean_tokens;
}

std::vector<double> TAnnotator::AnnotateCategory(const char *text) const {
    const std::string string_text = text;
    // Embedding
    std::vector<std::string> cleanText;
    cleanText = PreprocessText(string_text);

    // Prepare input for Naive Bayes
    std::vector<std::vector<std::string>> cleanTextList;
    cleanTextList.push_back(cleanText);

    std::vector<torch::jit::IValue> inputs;
    inputs.emplace_back(cleanTextList);

    // NB predict
    torch::IValue outputTensor;
    outputTensor = LANG.forward(inputs);

    auto categoryProba = outputTensor.toList().get(0).toGenericDict();
    std::vector<double> newProba;

    auto  it = categoryProba.begin();
    for (it = categoryProba.begin(); it != categoryProba.end(); it++) {
        double proba = it->value().toDouble();
        newProba.push_back(proba);
    }
    return newProba;
}
