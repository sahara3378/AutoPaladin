@echo off
:start

rem set /p k=请输入需要执行的项目名称(如Saas、划款)或测试计划id(metersphere)：
rem if "%k%" == "" (goto start)
rem python case_generator.py %k%

python case_generator.py 95540af8-a8d1-49fc-b395-fb9b3975bbb1
rd /S /Q D:\Autodeploy\paladin-test\AutoPaladin\case\allure\test
rd /S /Q D:\Autodeploy\paladin-test\AutoPaladin\case\allure\report
rem pytest --alluredir=allure\\test -k "%k%" -s
pytest --alluredir=allure\\test -s