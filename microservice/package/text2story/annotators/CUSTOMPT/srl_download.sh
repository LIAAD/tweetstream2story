#!/bin/bash


if [[ -d srl_bert_pt/srl-enpt_xlmr-large/ ]]
then
    echo "srl-enpt_xlmr-large exists on your filesystem."
else
    cd srl_bert_pt/
    python3.8 get_model.py srl-enpt_xlmr-large
    cd ..
fi

