#include "annotator.h"

#include <time.h>


#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/join.hpp>
#include <boost/locale.hpp>
#include <chrono>
#include <cmath>
#include <locale>
#include <optional>
#include <regex>
#include <string>

#include "boost/algorithm/string/regex.hpp"
#include "boost/regex.hpp"

//#define MEAUSRE_TIME

template <class DT = std::chrono::milliseconds,
          class ClockT = std::chrono::steady_clock>
class Timer {
 public:
  Timer(std::string const& name) : _name(name) { tick(); }
  ~Timer() {
    tock();
    printf("runtime[%s]: %ld ms \n", _name.c_str(), duration().count());
  }

 private:
  void tick() {
    _end = timep_t{};
    _start = ClockT::now();
  }

  void tock() { _end = ClockT::now(); }

  template <class T = DT>
  auto duration() const {
    //    gsl_Expects(_end != timep_t{} && "toc before reporting");
    return std::chrono::duration_cast<T>(_end - _start);
  }

 private:
  using timep_t = typename ClockT::time_point;
  timep_t _start = ClockT::now(), _end = {};

  std::string const _name;
};

static constexpr std::size_t ZERO_VALUE_SIZE_T = 0;
TAnnotator::TAnnotator(const std::string& langPath)
    : Tokenizer(onmt::Tokenizer::Mode::Conservative) {
  LANG = torch::jit::load(langPath);
  setlocale(LC_ALL, "rus");
  _listCleanTokensVec.push_back({});
  _inputsFlow.push_back({});
}

void TAnnotator::PreprocessText(const std::string& text) {
  // Remove links
  // std::regex
  // urlRe("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+");
  // std::string processed_text = std::regex_replace(text, urlRe, " ");

  // Tokenize
  std::vector<std::string>& vec = _listCleanTokensVec[0];
  Tokenizer.tokenize(text, vec);

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
  // std::string clean_token_string = boost::join(clean_tokens, " ");
}

int TAnnotator::AnnotateCategory(const char* text, std::size_t maxChars) {
#ifdef MEAUSRE_TIME
  Timer t("AnnotateCategory");
#endif
  auto const len = strlen(text);
  processing_text = &text[std::max(len - maxChars, ZERO_VALUE_SIZE_T)];

  // Embedding
  PreprocessText(processing_text);

  // Prepare input for Naive Bayes
  _inputsFlow[0] = _listCleanTokensVec;

  // NB predict

  auto const categoryProba = LANG.forward(_inputsFlow).toList();

  return categoryProba.get(0).toInt();
}
