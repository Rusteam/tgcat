#pragma once

#include "document.pb.h"

#include <nlohmann_json/json.hpp>

#include <string>
#include <vector>
#include <unordered_map>

class TDbDocument {
public:
    std::string FileName;
    std::string Url;
    std::string SiteName;
    std::string Host;

    uint64_t PubTime = 0;
    uint64_t FetchTime = 0;
    uint64_t Ttl = 0;

    std::string Title;
    std::string Text;
    std::string Description;

    std::string Language = "none";
    tg::ECategory Category = tg::ECategory::NC_UNDEFINED;

    using TEmbedding = std::vector<float>;
    std::unordered_map<tg::EEmbeddingKey, TEmbedding> Embeddings;

    std::vector<std::string> OutLinks;

    bool Nasty = false;

public:

    nlohmann::json ToJson() const;

    bool IsRussian() const { return Language == "ru"; }
    bool IsEnglish() const { return Language == "en"; }
    bool IsNews() const { return Category != tg::NC_NOT_NEWS && Category != tg::NC_UNDEFINED; }
    bool HasSupportedLanguage() const { return Language != "none"; }

    bool IsStale(uint64_t timestamp) const { return timestamp > FetchTime + Ttl; }
};
