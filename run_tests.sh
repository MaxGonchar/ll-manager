#!/bin/bash

# TODO: make running tests not dependent on the platform
# TODO: add possibility to rin one test
export LL_TESTING="1"
python -m unittest
unset LL_TESTING