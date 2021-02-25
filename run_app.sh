#!/bin/bash

python -m streamlit run src/train/app.py --server.address 0.0.0.0 --server.port ${PORT:-8501}