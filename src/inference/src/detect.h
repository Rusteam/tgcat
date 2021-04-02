#pragma once

#include "db_document.h"

namespace fasttext {
    class FastText;
}

struct TDocument;

std::string DetectLanguage(const fasttext::FastText& model, const TDocument& document);
