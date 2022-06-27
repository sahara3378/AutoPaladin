@echo off
rem 生成html格式的测试报告，需要把report目录放在web服务器如tomcat中访问
allure generate allure\\test -o allure\\report --clean