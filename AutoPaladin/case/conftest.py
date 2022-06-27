# coding=utf-8
import pytest

# 如果pytest-html报告结果用例编号出现乱码，可以通过修改 C:\Python37\Lib\site-packages\pytest_html\plugin.py文件中的部分：
# self.test_id = report.nodeid.encode("utf-8").decode("unicode_escape")
# 改成：
# self.test_id = report.nodeid
# 其它修改参考：http://www.likecs.com/show-71628.html

from tool import configs as conf
import os


def pytest_configure(config):
    config._metadata['测试环境'] = conf.get_config('browser', 'defaulturl')
    config._metadata['浏览器'] = conf.get_config('browser', 'type')
    config._metadata['日志文件'] = os.path.join(os.environ.get('AutoPaladin'), 'log', 'paladin-test.log')
    config._metadata['截图结果'] = '<a href=\"pics\\pics.html\">截图结果</a>'
    config._metadata['执行部门'] = '帕拉丁测试部'
    bu = os.environ.get('BUILD_USER')
    config._metadata['测试人员'] = bu if bu else '匿名用户'#获取jenkins构建者
    config._metadata.pop("JAVA_HOME")

    config.addinivalue_line('markers', '新股全节点流程测试')
    config.addinivalue_line('markers', '监管报表')
    config.addinivalue_line('markers', 'Saas')
    config.addinivalue_line('markers', '划款指令')
#
# @pytest.mark.optionalhook
# def pytest_html_results_summary(prefix):
#     prefix.extend([html.p("执行部门:帕拉丁测试部")])
#     prefix.extend([html.p("测试人员:张三")])
