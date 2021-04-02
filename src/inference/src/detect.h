#pragma once

#include "db_document.h"

namespace fasttext {
    class FastText;
}

struct TDocument;

// Change return type to string
std::string DetectLanguage(const fasttext::FastText& model, const TDocument& document);
