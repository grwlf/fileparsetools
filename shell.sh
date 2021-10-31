#!/bin/sh
export PYTHONPATH="./src:$PYTHONPATH"
nix-shell -p python3Packages.python python3Packages.ipython

