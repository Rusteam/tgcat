---
title: Tglang_programming_langugage_detection
app_file: app.py
sdk: gradio
sdk_version: 4.5.0
---
# Tglang - identify a programming language of a code snippet

[github repo]()

This is a solution for [Telegram hackathon](https://contest.com/docs/ML-Competition-2023-r2).

The list of supported languages:
```markdown
  TGLANG_LANGUAGE_C
  TGLANG_LANGUAGE_CPLUSPLUS
  TGLANG_LANGUAGE_CSHARP
  TGLANG_LANGUAGE_CSS
  TGLANG_LANGUAGE_DART
  TGLANG_LANGUAGE_DOCKER
  TGLANG_LANGUAGE_FUNC
  TGLANG_LANGUAGE_GO
  TGLANG_LANGUAGE_HTML
  TGLANG_LANGUAGE_JAVA
  TGLANG_LANGUAGE_JAVASCRIPT
  TGLANG_LANGUAGE_JSON
  TGLANG_LANGUAGE_KOTLIN
  TGLANG_LANGUAGE_LUA
  TGLANG_LANGUAGE_NGINX
  TGLANG_LANGUAGE_OBJECTIVE_C
  TGLANG_LANGUAGE_PHP
  TGLANG_LANGUAGE_POWERSHELL
  TGLANG_LANGUAGE_PYTHON
  TGLANG_LANGUAGE_RUBY
  TGLANG_LANGUAGE_RUST
  TGLANG_LANGUAGE_SHELL
  TGLANG_LANGUAGE_SOLIDITY
  TGLANG_LANGUAGE_SQL
  TGLANG_LANGUAGE_SWIFT
  TGLANG_LANGUAGE_TL
  TGLANG_LANGUAGE_TYPESCRIPT
  TGLANG_LANGUAGE_XML
```

Other programming languages and non-code text are identified
as `TGLANG_LANGUAGE_OTHER` (index 0).

## Model development

### Data

- Training data consisted of 3.7k+ files with 220k+ lines of code.
It consisted of files from the [Stack dataset](https://huggingface.co/datasets/bigcode/the-stack/viewer/default/train)
and manually collected from GitHub.
- Test set was manually labelled from [Telegram r1 files](https://data-static.usercontent.dev/ml2023-r1-dataset.tar.gz)
It consisted of 493 files and 7404 lines of code. Not all classes are present in the test set.
- Train files were split into shorter sequences of lines to 
match the test files' length. 
- OTHER files from the telegram files were added to the train set
to make up 20% of the data and to the test set to make up 50% of the data.

### Model


1. Tokenizer - a simple text tokenizer is used to extract
keywords and special characters from the code. Numbers,
comments and docstrings are removed.
2. Text embedding - a TfIdf vectorizer is used to extract
features from the train set. TfIdf params are:
```python
    max_features=1000,
    binary=True, 
    ngram_range=(1,1), 
    tokenizer=tokenize_text,
    lowercase=False,
```
3. Classifier - a simple multinomial naive bayes is trained on 
vectorizer output.

### Results

- Accuracy on the test set: 0.82
- Accuracy on the validation set: 0.83

