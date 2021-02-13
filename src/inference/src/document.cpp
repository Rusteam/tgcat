#include "document.h"
#include "util.h"

#include <boost/algorithm/string/predicate.hpp>
#include <boost/filesystem.hpp>

#include <sstream>
#include <fstream>

TDocument::TDocument(const nlohmann::json& json) {
    FromJson(json);
}

nlohmann::json TDocument::ToJson() const {
    nlohmann::json json({
        {"url", Url},
        {"site_name", SiteName},
        {"timestamp", FetchTime},
        {"title", Title},
        {"description", Description},
        {"file_name", CleanFileName(FileName)},
        {"text", Text},
    });
    if (!OutLinks.empty()) {
        json["out_links"] = OutLinks;
    }
    return json;
}

void TDocument::FromJson(const char* fileName) {
    std::ifstream fileStream(fileName);
    nlohmann::json json;
    fileStream >> json;
    FromJson(json);
}

void TDocument::FromJson(const nlohmann::json& json) {
    json.at("url").get_to(Url);
    json.at("site_name").get_to(SiteName);
    json.at("timestamp").get_to(FetchTime);
    json.at("title").get_to(Title);
    json.at("description").get_to(Description);
    json.at("text").get_to(Text);
    if (json.contains("file_name")) {
        json.at("file_name").get_to(FileName);
    }
    if (json.contains("out_links")) {
        json.at("out_links").get_to(OutLinks);
    }
}