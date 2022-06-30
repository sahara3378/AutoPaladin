# coding=utf-8
import imaplib, time
import email
#from idna import unicode

from tool import configs
from tool.logger import logger

conn = None
host = configs.get_config('email', 'email_host')
port = int(configs.get_config('email', 'email_port'))
user = configs.get_config('email', 'email_user')
pwd = configs.get_config('email', 'email_pwd')
sfolder = configs.get_config('email', 'email_folder')


def init():
    try:
        global conn
        conn = imaplib.IMAP4_SSL(host, port)
        conn.login(user, pwd)
        logger.info('已登录邮箱:%s' % user)
        return True
    except Exception as ex:
        logger.error('邮件初始化错误!',ex)
        return False


def _parse(message):
    subject = message.get('subject')
    dh = email.header.decode_header(subject)
    #subject = unicode(dh[0][0])
    subject = str(dh[0][0],encoding = 'utf-8')
    times = message.get('Date').replace(' +0800', '').replace(' (CST)', '').replace(' (GMT+08:00)', '')
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(times, '%a, %d %b %Y %H:%M:%S')), subject


def get_all_folder():
    """
    获取邮箱的所有文件夹；常用：INBOX、Drafts、Sent、Sent Messages、Deleted Messages"

    Returns:

    """
    if init():
        for x in conn.list()[1]:
            logger.info('文件夹:%s' % x)


def has_email(subject_key, folder=None, from_time='sysdate'):
    """
    判断邮箱是否存在指定标题的邮件

    Args:
        subject_key:邮件标题关键字
        from_time:从该时间点往后的邮件；如果传入'sysdate'则默认从当日0点往后；不传值默认'sysdate'
        folder:邮箱文件夹，默认从配置文件读取；不清楚邮箱文件夹的，使用get_all_folder获取

    Returns:

    """
    logger.info('邮件标题: %s ; 起始时间: %s ' % (subject_key, from_time))
    cnt = 0
    if from_time == 'sysdate':
        from_time = time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time()))
    try:
        from_timestamp = int(time.mktime(time.strptime(from_time, '%Y-%m-%d %H:%M:%S')))
    except Exception as ex:
        logger.error('时间参数错误!形如 2020-9-12 13:00:00',ex)
        return False

    if init():
        folder = folder if folder else sfolder
        try:
            conn.select(folder)
            typ, data = conn.search(None, '(FROM "")')
        except Exception as ex:
            logger.error('邮箱文件夹读取错误,文件夹：%s' % folder,ex)
            return False

        # 遍历邮件
        for num in data[0].split()[::-1]:
            typ, data = conn.fetch(num, '(RFC822)')
            times, subject = _parse(email.message_from_bytes(data[0][1]))
            e_timestamp = int(time.mktime(time.strptime(times, '%Y-%m-%d %H:%M:%S')))
            if e_timestamp < from_timestamp:
                logger.info('最新邮件[%s]时间[%s]小于起始时间[%s]' % (subject, times, from_time))
                break
            elif subject_key in subject and e_timestamp >= from_timestamp:
                logger.info('找到满足大于[%s]且标题包含[%s]的邮件！时间：[%s] 标题：[%s]' % (from_time, subject_key, times, subject))
                cnt += 1
    logger.info('条数%s' % cnt)
    return True if cnt > 0 else False


# def get_email(self):
#     pass
