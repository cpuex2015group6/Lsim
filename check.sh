#!/bin/bash

cur=`pwd`
pushd ../compiler/min-caml/test && cat ../libmincaml.ml check.ml > _check.ml && cd .. && make byte-code && ./min-caml test/_check > ./output && mv test/_check.s ${cur}/check.s && popd && ./native.sh check.s
