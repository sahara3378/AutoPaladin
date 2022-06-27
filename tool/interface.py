# coding=gbk
import requests, json

from tool import logger


def is_json(myjson):
    try:
        json.loads(myjson)
        return True
    except ValueError:
        return False


def getsession(url, login_params):
    try:
        session = requests.Session()
        response = session.post(url, login_params)
        if response.status_code == 200:
            response = json.loads(response.text)
            logger.info(response)
            if "��¼�ɹ���" in response['jsonStr']:
                logger.info('�ӿڵ�¼�ɹ�')
                return session
        else:
            logger.error('��¼���������:%s' % response.status_code)
    except Exception as ex:
        logger.error('��¼�����쳣:%s' % ex)


def send(url, params=None, session=None):
    try:
        if not session:
            session = requests.Session()
        if params:
            response = session.post(url, params)
        else:
            response = session.get(url)

        if response.status_code == 200:
            logger.info('�ӿ���ȷ��Ӧ')
            response = response.json() if is_json(response.text) else response.content.decode('utf-8')
            return response
        else:
            logger.error('�ӿ����������:%s %s' % (response.status_code, url))
            return None
    except Exception as ex:
        logger.error('�ӿ������쳣:%s' % url)
        logger.error(ex)
        return None


if __name__ == '__main__':
    # ��Saas��¼ʾ��
    param = {"name": "admin", "pwd": "1", "rememberme": "false"}
    session = getsession(
        'http://192.168.72.95:8087/scxx-web/userController/login?urlName=http://192.168.72.95:8087/scxx-web/paladin',
        param)

    # Saas��¼ʾ��
    param = {"name": "g7GKSSgDwc1gn8eRSvXToQ==", "pwd": "2f6DhqPBNoK3f2A7FFqAXA==", "sid": "org3",
             "rememberme": "false"}
    session = getsession(
        'http://192.168.72.100:8199/scxx-web/userController/login?urlName=http://192.168.72.100:8199/scxx-web/paladin?sid=org3',
        param)

    # �ӿ�ʾ��
    param = {"fDate": "2020-09-30"}
    logger.info(
        send('http://192.168.72.100:8199/scxx-web/reportScheduleController/dataGrid', param, session=session)['rows'][
            0])
