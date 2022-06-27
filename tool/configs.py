# coding=utf-8
import sys, os, base64
import traceback
from configparser import ConfigParser
from tool import logger

cp = None
spath = os.path.join(os.environ.get('AutoPaladin'), 'sys.cfg')


def read():
    global cp
    cp = ConfigParser()
    try:
        cp.read(spath, encoding="gb2312")
        return cp.sections()
    except Exception as ex:
        logger.error('读取系统配置文件sys.cfg失败')
        logger.error(ex)
        traceback.print_stack()
        sys.exit(1)


def set_config(section, key, value):
    """
    修改配置文件

    Args:
        section: 参数区域
        key: 参数名
        value: 参数值

    Returns:
        bool:是否成功
    """
    read()
    try:
        cp.set(section, key, value)
        cp.write(open(spath, 'w'))
        logger.info('修改了系统配置文件:%s.%s=%s' % (section, key, value))
        return True
    except Exception as ex:
        logger.error('修改系统配置文件sys.cfg失败')
        logger.error(ex)
        traceback.print_stack()
        return False


def get_config(section, key):
    """根据参数名，获取配置文件的参数值

        Args:
            section (str): 参数区域
            key (str): 参数名

        Returns:
            str: 参数值

        Examples:
            getconfig('browser','type') ，返回值：chrome

        """
    sections = read()
    for sec in sections:
        if sec == section:
            for item in cp.items(section):
                if item[0] == key:
                    if item[0] == 'email_pwd':  # 要加密的key值
                        try:
                            result = bytes.decode(base64.b64decode(item[1]))  # 先试试解密
                            return result
                        except:
                            # 如果是明文则加密并保存到配置文件
                            item_base = bytes.decode(base64.b64encode(item[1].encode("gb2312")))
                            set_config(section, key, item_base)
                    return item[1]
