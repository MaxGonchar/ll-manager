#!/bin/bash

export LL_TESTING="1"
python -m unittest
unset LL_TESTING