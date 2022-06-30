# -*- coding:gbk -*-
import os, json
import shutil
import time

from tool import configs, logger, dbms

ipo_jar = os.path.join(os.environ.get('AutoPaladin'), 'resource', 'mqtest.jar')
bak_path = configs.get_config('case', 'ipofile_path_bak')
ipo_path = configs.get_config('case', 'ipofile_path')


def restorefile():
    """
    还原备份目录下的文件到读取目录（因目前机器人读取文件后会删除）
    注意配置参数文件中的ipofile_path_bak、ipofile_path等参数

    Returns:

    """
    try:
        if not os.path.exists(ipo_path):
            os.makedirs(ipo_path)
        if os.path.exists(ipo_path):
            shutil.rmtree(ipo_path)
        shutil.copytree(bak_path, ipo_path)
        logger.info('已还原备份目录下的文件')
    except Exception as ex:
        logger.error('还原文件异常！',ex)


def get_paladin_config(key):
    """
    获取帕拉丁配置文件的参数值；注意需在sys.cfg正确配置配置文件

    Args:
        key: 参数名

    Returns:
        str: 参数值

    """
    config = configs.get_config('case', 'paladin_config')
    try:
        with open(config, 'r', encoding='utf8') as cg:
            for c in cg:
                if key in c:
                    return c.split('=')[-1].replace('\n', '')
    except Exception as ex:
        logger.error('获取帕拉丁配置文件异常！',ex)
    return None


def execute_ipo_tool(secCode, fileType, fileName, fileSource=''):
    """
    调用新股模拟测试工具

    Args:
        secCode: 股票代码
        fileType: 文件类型，如XJ_SH
        fileName: 文件名
        fileSource: 市场，SH 或 SZ

    Returns:
        bool:是否成功

    Examples:
        print(execute_ipo_tool('600078', 'SG_SH', r'600078申购数据1589946031376.xls'))
    """
    restorefile()
    assert len(secCode) == 6 and secCode.isdigit(), '股票代码格式错误'
    map = {'secName': '', 'isParse': '', 'attachmentId': ''}
    map['secCode'] = secCode
    map['fileType'] = fileType
    file = os.path.join(ipo_path, secCode, fileName)  # Z:\自动测试\600078\600078初步询价明细数据1589949462157.xls
    assert os.path.exists(file), '要读取的文件不存在:%s' % file
    if get_paladin_config('ipoConfig.useMongoDB') == 'true':
        map['fileUrl'] = dbms.upload_mongo_file(file)  # 如果是用mongodb的方式，fileUrl填写上传后的文件的id
    else:
        map['fileUrl'] = os.path.join(ipo_path, secCode, fileName)  # 否则填写文件路径
    map['fileName'] = fileName
    if fileSource:
        map['fileSource'] = fileSource
    else:
        map['fileSource'] = 'SH' if secCode.startswith('6') else 'SZ'
    return execute_ipo_tool_cus(json.dumps(map).replace(': ', '=').replace(', \"', ',\"').replace('\"', '\\"'))


def execute_ipo_tool_cus(customstr):
    """
    调用新股模拟测试工具

    Args:
        customstr: 满足json格式的字符串;注意参数中的空格要去掉，否则调用jar时会当做多个参数处理

    Returns:

    """
    try:
        cmd = 'java -jar %s %s' % (ipo_jar, customstr)
        logger.info('执行命令:%s' % cmd)
        i = os.system(cmd)
        logger.info('读取ipo文件此处强制设置等待30秒')
        time.sleep(30)
        return True if i == 0 else False
    except Exception as ex:
        logger.error("调用新股模拟测试工具异常！",ex)
        return False


def execute_cmd(cmdstrs):
    """
    执行操作系统命令

    Args:
        cmdstrs: cmd命令行，多个语句以回车分隔

    Returns:

    """
    try:
        for cmdstr in cmdstrs.split('\n'):
            logger.info('执行Windows命令:%s' % cmdstr)
            if os.system(cmdstr) != 0:
                return False
        return True
    except Exception as ex:
        logger.error("执行操作系统命令异常！",ex)
        return False


if __name__ == '__main__':
    pass
    print(execute_ipo_tool('600078', 'SG_SH', r'600078申购数据1589946031376.xls'))
