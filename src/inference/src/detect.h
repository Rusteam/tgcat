#pragma once

#include "db_document.h"

namespace fasttext {
    class FastText;
}

struct TDocument;

tg::ELanguage DetectLanguage(const fasttext::FastText& model, const TDocument& document);
