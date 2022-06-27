# coding=utf-8
import json
import sys, os
import traceback
import pymysql

from tool import logger, configs


def initdb():
    global db, cur
    try:
        db = pymysql.connect(host=configs.get_config('metersphere', 'host'), \
                             port=int(configs.get_config('metersphere', 'port')), \
                             user=configs.get_config('metersphere', 'user'), \
                             password=configs.get_config('metersphere', 'password'), \
                             database=configs.get_config('metersphere', 'database'), \
                             charset='utf8')
        cur = db.cursor()
    except Exception as ex:
        logger.error(ex)
        traceback.print_stack()


def updatedb(sql):
    try:
        logger.debug(sql)
        cur.execute(sql)
        db.commit()
    except Exception as ex:
        logger.error(ex)
        traceback.print_stack()


def update_plan(plan_id):
    # key为allure value为metersphere
    sta_dic = {"passed": "Pass", "failed": "Failure", "Blocking": "Blocking", "Skip": "Skip"}
    if plan_id:
        initdb()
        # 更新该计划下自动测试用例的结果为“未开始”
        updatedb(
            'update test_plan_test_case set status=\'Prepare\' where plan_id=\'{plan_id}\' and case_id in (select id from test_case where method=\'auto\')')
        jsonfile = os.path.join(os.environ.get('AutoPaladin'),'case','allure','report','data','behaviors.json')
        if not os.path.exists(jsonfile):
            logger.error('allure报告不存在')
            sys.exit(1)
        with open(jsonfile, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
            cases = json_data.get('children')
            for case in cases:
                case_id = case.get('name').split('_')[-1]
                # allure的状态转换为metersphere的状态
                status = sta_dic.get(case.get('status'))
                import time;
                current_time = int(str(time.time()).replace('.', '')[0:13])
                updatedb(
                    'update test_plan_test_case set status=\'{status}\',update_time={ct} where plan_id=\'{plan_id}\' and case_id=\'{case_id}\''.format(
                        status=(status), ct=current_time, plan_id=plan_id, case_id=case_id))
                logger.info('用例【{case}】的状态更新为{status}'.format(case=case.get('name'), status=status))
            db.close()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        update_plan(sys.argv[1])
        logger.info('更新计划[%s]的执行结果！' % sys.argv[1])
    else:
        logger.info('更新用例结果失败，未传入计划id！')
        sys.exit(1)
