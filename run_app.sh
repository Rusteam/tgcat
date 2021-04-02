#!/bin/bash

python -m streamlit run src/train/app.py
=======
# lid model
mkdir -p models/external
LID_FILE=models/external/lid.176.bin
if test -f $LID_FILE; then
  echo "$LID_FILE exists"
else
  echo "downloading $LID_FILE"
  curl https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin -o $LID_FILE
fi

# tgcat models
mkdir -p models/trained/tgcat
TGCAT_EN=models/trained/tgcat/en_tgcat.pt
if test -f $TGCAT_EN; then
  echo "$TGCAT_EN exists"
else
  echo "downloading $TGCAT_EN"
  curl https://transfer.sh/Ow7mQ/en_tgcat.pt -o $TGCAT_EN
fi
TGCAT_RU=models/trained/tgcat/ru_tgcat.pt
if test -f $TGCAT_RU; then
  echo "$TGCAT_RU exists"
else
  echo "downloading $TGCAT_RU"
  curl https://transfer.sh/yl0Bj/ru_tgcat.pt -o $TGCAT_RU
fi

# ref data
mkdir -p data/processed
REF_0212=data/processed/dc0212-input_reference.json
if test -f $REF_0212; then
  echo "$REF_0212 exists"
else
  echo "downloading $REF_0212"
  curl https://transfer.sh/NSSdt/dc0212-input_reference.json -o $REF_0212
fi
REF_0206=data/processed/dc0206-input_reference.json
if test -f $REF_0206; then
  echo "$REF_0206 exists"
else
  echo "downloading $REF_0206"
  curl https://transfer.sh/ufG1y/dc0206-input_reference.json -o $REF_0206
fi

python -m streamlit run src/train/app.py --server.address 0.0.0.0 --server.port ${PORT:-8501}
