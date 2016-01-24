#!/bin/bash

cur=`pwd`
pushd ../compiler/min-caml/min-rt && cat ../libmincaml.ml globals.ml min-rt.ml > hoge.ml && cd .. && make byte-code && ./min-caml min-rt/hoge > ./output && mv min-rt/hoge.s ${cur}/hogehoge.s && popd && ./native.sh hogehoge.s
