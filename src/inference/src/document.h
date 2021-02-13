#pragma once

#include <nlohmann_json/json.hpp>

#include <string>
#include <vector>
#include <cstdint>


// Original fields only
struct TDocument {
public:
    std::string Title;
    std::string Url;
    std::string SiteName;
    std::string Description;
    std::string FileName;
    std::string Text;
    std::string Author;

    uint64_t PubTime = 0;
    uint64_t FetchTime = 0;

    std::vector<std::string> OutLinks;

public:
    TDocument() = default;
    explicit TDocument(const nlohmann::json& json);

    nlohmann::json ToJson() const;
    void FromJson(const char* fileName);
    void FromJson(const nlohmann::json& json);
};
