# AutoPaladin
1.环境变量设置
AutoPaladin,指向项目代码所在路径
PYTHONPATH,变量值增加%AutoPaladin%

2.安装依赖包
python -m pip install --upgrade pip
pip install pymysql
pip install selenium
pip install cx_Oracle
	如果提示cx_Oracle.DatabaseError: DPI-1047，将Oracle客户端安装路径下的 
	oci.dll  oraocci11.dll  oraociei11.dll这三个文件拷贝到python安装路径的LIB/site-packages下
pip install pymongo
pip install requests
pip install allure-pytest
pip install pytest-metadata

3.安装allure
下载：https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/
增加到%PATH%环境变量中：D:\app\allure-2.18.1\bin

