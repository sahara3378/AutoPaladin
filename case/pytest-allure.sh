#!/bin/bash
read -p "input keyword:" keyword
python case_generator.py $keyword
/bin/rm -fr allure/test
/bin/rm -fr allure/report
python -m pytest --alluredir=allure/test -k $keyword -s
