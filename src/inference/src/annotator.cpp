#include "annotator.h"
#include "detect.h"
#include "document.h"
#include "nasty.h"
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
        const std::string& modelPath,
        const std::string& vocabularyRUPath,
        const std::string& vocabularyENPath,
        const std::string& nbRUPath,
        const std::string& nbENPath,
        size_t maxWords) :
        RUEmbedder(vocabularyRUPath, maxWords),
        ENEmbedder(vocabularyRUPath, maxWords),
        Tokenizer(onmt::Tokenizer::Mode::Conservative, onmt::Tokenizer::Flags::CaseFeature)
{
    LanguageDetector.loadModel(modelPath);
    RUNB = torch::jit::load(nbRUPath);
    ENNB = torch::jit::load(nbENPath);
}


std::optional<TDbDocument> TAnnotator::AnnotateLanguage(TDocument& document) const {
    TDbDocument dbDoc;
    std::regex urlRe("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+");
    std::string processed_text = std::regex_replace(document.Text, urlRe, " ");
    document.Text = processed_text;

    dbDoc.Language = DetectLanguage(LanguageDetector, document);
    return dbDoc;
}


std::vector<std::string> TAnnotator::PreprocessText(const std::string& text, bool isRU) const {
    setlocale(LC_ALL, "rus");
    // Remove links
    std::regex urlRe("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+");
    std::string processed_text = std::regex_replace(text, urlRe, " ");

    // Tokenize
    std::vector<std::string> tokens;
    Tokenizer.tokenize(processed_text, tokens);

    // Leave only russian words
    std::vector<std::string> clean_tokens;
    boost::regex xRegEx;
    if (isRU){
        xRegEx = boost::regex("[абвгдеёжзийклмнопрстуфхцчшщъыьэюя]+");
    } else {
        xRegEx = boost::regex("[a-z]+");
    }
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

at::Dict<std::string, double> TAnnotator::AnnotateCategory(TDocument &document) const {
    std::optional<TDbDocument> dbDoc = AnnotateLanguage(document);
    if (!dbDoc->IsEnglish() and !dbDoc->IsRussian()){
        at::Dict<std::string, double> newProba;
        newProba.insert("Art & Design", 0.0);
        return newProba;
    }

    std::vector<std::string> cleanText;
    // Embedding
    if (dbDoc->IsEnglish()){
        cleanText = PreprocessText(document.Text, false);
    }
    if (dbDoc->IsRussian()){
        cleanText = PreprocessText(document.Text, true);
    }
    // Prepare input for Naive Bayes
    std::vector<std::vector<std::string>> cleanTextList;
    cleanTextList.push_back(cleanText);

    std::vector<torch::jit::IValue> inputs;
    inputs.emplace_back(cleanTextList);

    // NB predict
    at::IValue outputTensor;
    if (dbDoc->IsEnglish()){
        outputTensor = ENNB.forward(inputs);
    }
    if (dbDoc->IsRussian()){
        outputTensor = RUNB.forward(inputs);
    }
    auto categoryProba = outputTensor.toList().get(0).toGenericDict();
    at::Dict<std::string, double> newProba;

    auto  it = categoryProba.begin();
    for (it = categoryProba.begin(); it != categoryProba.end(); it++) {
        // Round to 2 decimals after point
        double proba = it->value().toDouble();
        proba = std::floor((proba * 100) + .5) / 100;
        newProba.insert(it->key().toStringRef(), proba);
    }
    return newProba;
}
