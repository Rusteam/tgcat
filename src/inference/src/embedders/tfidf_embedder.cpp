#include "tfidf_embedder.h"
#include "../util.h"

#include <sstream>
#include <cassert>

TTfIdfEmbedder::TTfIdfEmbedder(
    const std::string& vocabularyPath
    , size_t maxWords
)
    : TokenIndexer(vocabularyPath, maxWords)
    , Idfs(TokenIndexer.Size())
{
    std::ifstream vocabFile(vocabularyPath);
    std::string line;
    size_t wordIndex = 0;
    while (std::getline(vocabFile, line)) {
        std::string idfString = line.substr(line.find('\t') + 1);
        float idf = std::stof(idfString);
        Idfs[wordIndex] = idf;
        wordIndex++;
    }
}

std::vector<float> TTfIdfEmbedder::CalcEmbedding(const std::string& input) const {
    std::vector<size_t> indices = TokenIndexer.Index(input);
    std::unordered_map<size_t, size_t> wordsCounts;
    for (size_t wordIndex : indices) {
        wordsCounts[wordIndex] += 1;
    }
    std::vector<float> tfIdfVector(TokenIndexer.Size());
    for (const auto& [wordIndex, wordCount] : wordsCounts) {
        float tf = static_cast<float>(wordCount) / static_cast<float>(indices.size());
        tfIdfVector[wordIndex] = tf * Idfs[wordIndex];
    }

    return tfIdfVector;
}
