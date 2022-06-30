import cx_Oracle, pymysql
import os

from gridfs import GridFS
from pymongo import MongoClient

from tool import logger, configs

db = None


#     """
#     如果提示cx_Oracle.DatabaseError: DPI-1047: Cannot locate a 32-bit Oracle Client library
#     将Oracle客户端安装路径下的 oci.dll  oraocci11.dll  oraociei11.dll这三个文件拷贝到python安装路径的LIB/site-packages下
#     """

def init():
    """
    初始化数据库，数据库的配置信息获取配置文件db区域

    Returns:

    """
    global db
    if db:
        try:
            db.close()
        except Exception as ex:
            logger.error('关闭数据库连接异常',ex)
    try:
        dbtyype = configs.get_config('db', 'type')
        logger.info('初始化数据库...%s' % dbtyype)
        if dbtyype == 'oracle':
            db = cx_Oracle.connect(configs.get_config('oracle', 'db'))
        elif dbtyype == 'mysql':
            db = pymysql.connect(host = configs.get_config('mysql', 'host'), \
                                user = configs.get_config('mysql', 'user'), \
                                password = configs.get_config('mysql', 'passwd'), \
                                database = configs.get_config('mysql', 'db'), \
                                charset='utf8')
    except Exception as ex:
        logger.error('初始化数据库失败',ex)
        


def query(sql):
    """
    查询数据库

    Args:
        sql: 执行的sql语句

    Returns:
        list[dict1,dict2]:返回单个数据值,如：12；或多行数据的集合,例如[{'NAME': 'test1', 'ID': '1'},{'NAME': 'test2', 'ID': '2'},{'NAME': 'test3', 'ID': '3'}]
    """
    try:
        init()
        cur = db.cursor()
        logger.debug('执行sql语句：%s' % sql)
        cur.execute(sql)
        col_names = [i[0] for i in cur.description]
        result = [dict(zip(col_names, row)) for row in cur]
        cur.close()
        if len(result) == 1:
            if (len(result[0])) == 1:
                for x in result[0].keys():
                    return result[0][x]

        return result
    except Exception as ex:
        logger.error('查询数据库异常！',ex)


def update(sql, params=None):
    """
    更新数据库

    Args:
        sql: 更新语句
        params: 参数

    Returns:
        bool:是否成功
    """
    try:
        init()
        cur = db.cursor()
        for s in sql.split('\n'):
            if params:
                cur.execute(s, params)
            else:
                cur.execute(s)
            logger.info('执行sql:%s 参数%s' % (sql, params))
        db.commit()
        cur.close()
        return True
    except Exception as ex:
        logger.error('更新数据库失败 %s' % sql,ex)
        return False


def del_mongo_file(filename):
    """
    删除mongodb中的文件，mongodb配置从配置文件获取

    Args:
        filename: 文件名包含filename关键字的才删除

    Returns:
        bool:是否成功
    """
    try:
        client = MongoClient(configs.get_config('mongodb', 'url'))
        db = client[configs.get_config('mongodb', 'db')]

        fs = GridFS(db)
        files = fs.find()

        for file in files:
            if filename in file.filename:
                fs.delete(file._id)
                logger.info('删除mongodb附件【%s】，id【%s】' % (file.filename, file._id))

        return True
    except Exception as ex:
        logger.error('删除mongodb附件失败！',ex)
        return False


def upload_mongo_file(filename):
    """
    上传本地文件到mongodb中，mongodb配置从配置文件获取

    Args:
        filename: 完整文件路径，如 C:\Windows\system.ini

    Returns:
        object:上传成功返回文件id，否则返回None
    """
    if not os.path.exists(filename):
        logger.error('附件不存在！%s' % filename)
        return None
    try:
        client = MongoClient(configs.get_config('mongodb', 'url'))
        db = client[configs.get_config('mongodb', 'db')]
        fs = GridFS(db)
        dic = dict()
        dic['filename'] = filename.split('\\')[-1]
        from datetime import datetime
        content = open(filename, 'rb').read()  # 二进制格式读取文件内容
        id = str(fs.put(content, **dic))  # 上传文件
        if id:
            logger.info('上传了mongodb附件:%s; id:%s' % (filename, id))
            return id
    except Exception as ex:
        logger.error('上传mongodb附件失败！%s' % filename,ex)
        return None


def execproc(procname, params=None):
    """
    执行存储过程

    Args:
        procname:存储过程名称
        params:参数

    Returns:

    """
    init()
    cur = db.cursor()
    error_c = cur.var(cx_Oracle.STRING)
    error_m = cur.var(cx_Oracle.STRING)
    params.append(error_c)
    params.append(error_m)
    try:
        error_c, error_m = cur.callproc(procname, params)
    except Exception as ex:
        logger.error('执行存储过程失败 %s %s' % (procname, params),ex)
    db.commit()
    cur.close()
    return error_c.getvalue(), error_m.getvalue()


if __name__ == '__main__':
    # mysql
    configs.set_config('db','type','mysql')
    update('update pldweb_cs3.tuser set fax=\'43\'')
    print(query('select name from pldweb_cs3.tuser where name like \'%sah%\''))

    # oracle
    configs.set_config('db','type','oracle')
    configs.set_config('oracle','db','reporter/rpt_cs2020@192.168.72.92:1521/orcl')
    update('update a set b=3')
    print(query('select name,id from tuser where name like \'%sah2%\''))

    # mongodb
    # print(upload_mongo_file(r'C:\Windows\system.ini'))
