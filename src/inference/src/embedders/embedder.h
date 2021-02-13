#pragma once

#include "config.pb.h"
#include "enum.pb.h"

class TEmbedder {
public:
    explicit TEmbedder() {}

    virtual std::vector<float> CalcEmbedding(const std::string& input) const = 0;

protected:
    tg::EEmbedderField Field;
};
