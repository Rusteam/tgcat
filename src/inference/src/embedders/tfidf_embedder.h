#pragma once

#include "embedder.h"
#include "token_indexer.h"

class TTfIdfEmbedder {
public:
    TTfIdfEmbedder(const std::string& vocabularyPath, size_t maxWords);

    std::vector<float> CalcEmbedding(const std::string& input) const;

private:
    TTokenIndexer TokenIndexer;
    std::vector<float> Idfs;
};
