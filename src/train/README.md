
# Training models


### Trained models
- text vectorization: Tf-Idf, Bag-of-words
- classification: Multinomial/Complement NB

### Model details

##### Inputs


A list (batch) of preprocessed and tokenized list of tokens as **List[List[str]]**
example: 

    [['team', 'ah', 'vip', 'tool', 'free', 'key', 'for', 'everyone', 'global'],
     ['sports', 'expert', 'to', 'help', 'you', 'high', 'investment',]]
     
##### Outputs

**List[Dict[str, float]]**

    [
        {'Education': 0.5303325652226045, 'Foreign Languages': 0.23760836574825156, 'Travel & Tourism': 0.23205906902914397},
        {'Education': 0.5303325652226045, 'Foreign Languages': 0.23760836574825156, 'Travel & Tourism': 0.23205906902914397},
    ]


##### Model files

    models/trained/tgcat/en_tgcat.pt
    models/trained/tgcat/ru_tgcat.pt
    
    
##### Sample prediction

    src/train/predict.py

##### Test files

    data/processed/en_predictions.json      
    data/processed/ru_predictions.json
    
### Use models

The vectorizer and the classifier saved as [TorchScript](https://pytorch.org/docs/stable/jit.html)

```python
import torch

filepath = "path/to/model.pt"

scripted_model = torch.jit.load(filepath)
out = scripted_model(inputs)
```


### Steps

1. Clean text: remove URLs, lowercase
2. Tokenize: get tokens, filter out non-word and one-char tokens
3. Join tokens: join title, description, recent_posts with '\n'
3. Vectorize texts to get word embeddings
4. Classify to get probabilities of each topic
5. Take top 2
6. Normalize probabilities to sum up to one


