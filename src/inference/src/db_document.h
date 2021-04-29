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

    std::string Language = "none";  // Change to string
    tg::ECategory Category = tg::ECategory::NC_UNDEFINED;

    using TEmbedding = std::vector<float>;
    std::unordered_map<tg::EEmbeddingKey, TEmbedding> Embeddings;

    std::vector<std::string> OutLinks;

    bool Nasty = false;

public:

    nlohmann::json ToJson() const;
    // Remove unused methods
    bool IsRussian() const { return Language == "ru"; }  // Change to comparison with string
    bool IsEnglish() const { return Language == "en"; }  // Change to comparison with string
    bool IsArabic() const { return Language == "ar"; }  // Change to comparison with string
    bool IsFarsi() const { return Language == "fa"; }  // Change to comparison with string
    bool IsUzbek() const { return Language == "uz"; }  // Change to comparison with string
    bool IsNews() const { return Category != tg::NC_NOT_NEWS && Category != tg::NC_UNDEFINED; }
    bool HasSupportedLanguage() const { return Language != "none"; }

    bool IsStale(uint64_t timestamp) const { return timestamp > FetchTime + Ttl; }
};
