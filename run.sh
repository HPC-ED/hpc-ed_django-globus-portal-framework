#!/bin/zsh

eval "$(conda shell.zsh hook)"
conda activate hpced

conda activate hpced
export APP_CONFIG='dgpf1/local_settings.py'
python dgpf1/manage.py migrate
python dgpf1/manage.py loaddata initial_providers
open -a Google\ Chrome http://127.0.0.1:8000/
python dgpf1/manage.py runserver
