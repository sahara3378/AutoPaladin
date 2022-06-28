# AutoPaladin
* ```AutoPaladin```是基于```Python```编写的针对帕拉丁系统的UI测试框架，封装了帕拉丁系统登录、打开菜单、点击按钮、输入文本框、下拉框选中、表格操作等常规操作，使得UI测试变得**简易化**。
* 另外针对开源工具```metersphere```进行了改造，支持在其上面编写满足```AutoPaladin```格式的UI自动化测试用例及测试计划，使得UI测试用例编写**可视化、系统化**。
* 断言支持消息提示、页面元素判断、表格内容判断、数据库内容判断、邮件内容判断等。
* 支持异常情况截图保存。
* 非常规操作支持编写自定义python脚本。
## 1.环境变量设置
* ```AutoPaladin```指向项目代码所在路径
* ```PYTHONPATH``` 变量值增加%AutoPaladin%

## 2.安装依赖包
* python -m pip install --upgrade pip
* pip install pymysql
* pip install selenium
* pip install cx_Oracle
  * ```如果提示cx_Oracle.DatabaseError: DPI-1047，将Oracle客户端安装路径下的oci.dll  oraocci11.dll  oraociei11.dll这三个文件拷贝到python安装路径的LIB/site-packages下```
* pip install pymongo
* pip install requests
* pip install allure-pytest
* pip install pytest-metadata

## 3.安装allure
* 下载：https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/
* D:\app\allure-2.18.1\bin增加到```PATH```环境变量中：

## 4.使用示例
from paladin import Paladin  
from paladin.type import Ele  
p=Paladin('http://192.168.72.95:8096/scxx-web/paladin','auto','1','chrome')  
p.open('报送管理-监管报表报送')  
p.find(Ele.INPUT,'业务日期').do('2022-06-22')  
p.find(Ele.BUTTON,'查询').do()  
cnt=p.find(Ele.DATAGRID).total()  
print(cnt)  
p.logout()