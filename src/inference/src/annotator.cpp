#include "annotator.h"

#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/join.hpp>
#include <boost/locale.hpp>
#include <cmath>
#include <locale>
#include <optional>
#include <regex>
#include <string>

#include "boost/algorithm/string/regex.hpp"
#include "boost/regex.hpp"

TAnnotator::TAnnotator(const std::string& langPath)
    : Tokenizer(onmt::Tokenizer::Mode::Conservative) {
  LANG = torch::jit::load(langPath);
  setlocale(LC_ALL, "rus");
}

std::vector<std::string> TAnnotator::PreprocessText(
    const std::string& text) const {

  // Tokenize
  std::vector<std::string> tokens;
  Tokenizer.tokenize(text, tokens);

 return tokens;
}

int TAnnotator::AnnotateCategory(const char* text, int maxChars) const {
  int len = strlen(text);
  std::string processing_text{&text[std::max(len - maxChars, 0)]};

  // Embedding
  std::vector<std::string> cleanText{PreprocessText(processing_text)};

  // Prepare input for Naive Bayes
  std::vector<std::vector<std::string>> cleanTextList(1, cleanText);
  std::vector<torch::jit::IValue> inputs(1, cleanTextList);

  // NB predict
  torch::IValue outputTensor{LANG.forward(inputs)};

  auto categoryProba = outputTensor.toList();

  return categoryProba.get(0).toInt();
}