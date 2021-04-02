#include "db_document.h"
#include "util.h"

// Remove unused methods

nlohmann::json TDbDocument::ToJson() const {
    nlohmann::json json({
        {"url", Url},
        {"site_name", SiteName},
        {"timestamp", FetchTime},
        {"title", Title},
        {"description", Description},
        {"file_name", CleanFileName(FileName)},
        {"text", Text},
        {"language", Language},
        {"category", Category}
    });
    if (!OutLinks.empty()) {
        json["out_links"] = OutLinks;
    }
    return json;
}

