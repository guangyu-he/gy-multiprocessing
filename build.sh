#!/bin/zsh

source ./venv/bin/activate

rm ./dist/*
python3 setup.py sdist
twine upload ./dist/*

deactivate
