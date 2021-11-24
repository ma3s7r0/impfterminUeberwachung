#!/bin/sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp impf-configuration.env.sample impf-configuration.env
chmod +x impfueberwachung.py