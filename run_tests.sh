#!/bin/bash

# TODO: make running tests not dependent on the platform
export LL_TESTING="1"
python -m unittest
unset LL_TESTING