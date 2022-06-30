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
    ��ԭ����Ŀ¼�µ��ļ�����ȡĿ¼����Ŀǰ�����˶�ȡ�ļ����ɾ����
    ע�����ò����ļ��е�ipofile_path_bak��ipofile_path�Ȳ���

    Returns:

    """
    try:
        if not os.path.exists(ipo_path):
            os.makedirs(ipo_path)
        if os.path.exists(ipo_path):
            shutil.rmtree(ipo_path)
        shutil.copytree(bak_path, ipo_path)
        logger.info('�ѻ�ԭ����Ŀ¼�µ��ļ�')
    except Exception as ex:
        logger.error('��ԭ�ļ��쳣��',ex)


def get_paladin_config(key):
    """
    ��ȡ�����������ļ��Ĳ���ֵ��ע������sys.cfg��ȷ���������ļ�

    Args:
        key: ������

    Returns:
        str: ����ֵ

    """
    config = configs.get_config('case', 'paladin_config')
    try:
        with open(config, 'r', encoding='utf8') as cg:
            for c in cg:
                if key in c:
                    return c.split('=')[-1].replace('\n', '')
    except Exception as ex:
        logger.error('��ȡ�����������ļ��쳣��',ex)
    return None


def execute_ipo_tool(secCode, fileType, fileName, fileSource=''):
    """
    �����¹�ģ����Թ���

    Args:
        secCode: ��Ʊ����
        fileType: �ļ����ͣ���XJ_SH
        fileName: �ļ���
        fileSource: �г���SH �� SZ

    Returns:
        bool:�Ƿ�ɹ�

    Examples:
        print(execute_ipo_tool('600078', 'SG_SH', r'600078�깺����1589946031376.xls'))
    """
    restorefile()
    assert len(secCode) == 6 and secCode.isdigit(), '��Ʊ�����ʽ����'
    map = {'secName': '', 'isParse': '', 'attachmentId': ''}
    map['secCode'] = secCode
    map['fileType'] = fileType
    file = os.path.join(ipo_path, secCode, fileName)  # Z:\�Զ�����\600078\600078����ѯ����ϸ����1589949462157.xls
    assert os.path.exists(file), 'Ҫ��ȡ���ļ�������:%s' % file
    if get_paladin_config('ipoConfig.useMongoDB') == 'true':
        map['fileUrl'] = dbms.upload_mongo_file(file)  # �������mongodb�ķ�ʽ��fileUrl��д�ϴ�����ļ���id
    else:
        map['fileUrl'] = os.path.join(ipo_path, secCode, fileName)  # ������д�ļ�·��
    map['fileName'] = fileName
    if fileSource:
        map['fileSource'] = fileSource
    else:
        map['fileSource'] = 'SH' if secCode.startswith('6') else 'SZ'
    return execute_ipo_tool_cus(json.dumps(map).replace(': ', '=').replace(', \"', ',\"').replace('\"', '\\"'))


def execute_ipo_tool_cus(customstr):
    """
    �����¹�ģ����Թ���

    Args:
        customstr: ����json��ʽ���ַ���;ע������еĿո�Ҫȥ�����������jarʱ�ᵱ�������������

    Returns:

    """
    try:
        cmd = 'java -jar %s %s' % (ipo_jar, customstr)
        logger.info('ִ������:%s' % cmd)
        i = os.system(cmd)
        logger.info('��ȡipo�ļ��˴�ǿ�����õȴ�30��')
        time.sleep(30)
        return True if i == 0 else False
    except Exception as ex:
        logger.error("�����¹�ģ����Թ����쳣��",ex)
        return False


def execute_cmd(cmdstrs):
    """
    ִ�в���ϵͳ����

    Args:
        cmdstrs: cmd�����У��������Իس��ָ�

    Returns:

    """
    try:
        for cmdstr in cmdstrs.split('\n'):
            logger.info('ִ��Windows����:%s' % cmdstr)
            if os.system(cmdstr) != 0:
                return False
        return True
    except Exception as ex:
        logger.error("ִ�в���ϵͳ�����쳣��",ex)
        return False


if __name__ == '__main__':
    pass
    print(execute_ipo_tool('600078', 'SG_SH', r'600078�깺����1589946031376.xls'))
