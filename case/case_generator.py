# coding=utf-8
import json
import os
import shutil
import sys
import time
import pymysql

from tool import logger, configs
from paladin.type import *

with open('varnamefile.txt','r',encoding='utf-8') as f:
    vardata=eval(f.read())

def _generate_script(repstr):
    """
    格式化用例编写的自定义脚本，补齐try/catch，以及处理脚本占位符合用例脚本
    Args:
        repstr: 输入脚本

    Returns:
        处理过后的脚本
    """
    result = []
    lines = repstr.split('\n')
    for line in lines:
        hasletter = False
        result_line = []
        for s in line:
            if s == ' ' and not hasletter:  # 行首的空格替换成Tab占位
                result_line.append('\t')
            else:
                hasletter = True
                result_line.append(s)
        result.append('\t\t\t' + ''.join(result_line))
    result = ['\t\ttry:'] + result + ['\t\texcept Exception as ex:', '\t\t\tlogger.error(\'执行自定义脚本发生异常！\' , ex)',
                                      '\t\t\tfrom paladin.type import ExpectType',
                                      '\t\t\tself.paladin.get_expect(ExpectType.TAKESCREEN,\'%s_自定义脚本异常\' % case[\'用例编号\'])',
                                      '\t\t\tassert False']
    result = '\n'.join(result)
    return result


def _get_variable(varname):
    """
    解析变量，例如[sysdate]返回YYYY-MM-DD

    Args:
        varname:[变量名]

    Returns:
        变量值，若格式不正确或不支持的变量，直接返回原值

    """
    if varname is None:
        return None

    if isinstance(varname, str):
        # varname = str(varname)
        if varname.startswith('[') and varname.endswith(']'):
            v = varname[1:-1]
            if v == 'sysdate':  # 系统日期：2020-11-11
                return time.strftime('%Y-%m-%d', time.localtime(time.time()))
            elif v == 'sysdate_scope':  # 系统日期区间：2020-11-11 - 2020-11-11
                return _get_variable('[sysdate]') + ' - ' + _get_variable('[sysdate]')
            elif v in vardata:
                return vardata[v]
            else:
                logger.warn('%s 为变量形式，但不支持解析，返回原值' % varname)
                return varname
        elif '\nreturn' in varname:  # 执行自定义代码块获取结果，注意必须有return
            try:
                script = 'def test():\n' + _generate_script(varname)
                constant = globals().copy()
                exec(script, constant)
                return constant['test']()
            except Exception as ex:
                logger.error('执行自定义代码块出现异常！',ex)
                return None
        else:
            return varname
    else:
        return varname


class CaseGenerator:
    """
    测试用例脚本生成器
    可根据计划id获取用例，或根据项目名称获取
    """

    def __init__(self, case_keyword):
        self.case_keyword = case_keyword
        self._get_cases()

    def _get_cases(self):
        """
        读取数据库的用例

        Returns:

        """
        try:
            db = pymysql.connect(host=configs.get_config('metersphere', 'host'), \
                                 port=int(configs.get_config('metersphere', 'port')), \
                                 user=configs.get_config('metersphere', 'user'), \
                                 password=configs.get_config('metersphere', 'password'), \
                                 database=configs.get_config('metersphere', 'database'), \
                                 charset='utf8')
            sql_plan = 'select p.name as project_name, c.node_path, c.name,c.id, concat(c.num,\'\') as case_num,  ' \
                       'c.pre_type, c.prerequisite, c.steps, c.remark               ' \
                       '  from test_plan_test_case pc                               ' \
                       ' inner join test_case c                                     ' \
                       '    on pc.case_id = c.id                                    ' \
                       ' inner join project p                                       ' \
                       '    on p.id = c.project_id                                  ' \
                       ' inner join test_case_node n                                       ' \
                       '    on n.id = c.node_id                                  ' \
                       ' where pc.plan_id = \'{plan_id}\'  						 ' \
                       '   and c.method = \'auto\'                                  ' \
                       '   and c.type = \'functional\'                              ' \
                       ' order by n.pos, c.num                                '.format(
                plan_id=self.case_keyword)
            logger.debug(sql_plan)
            sql_project = 'select p.name as project_name, c.node_path, c.name, c.id,         ' \
                          'concat(c.num, \'\') as case_num, c.pre_type, c.prerequisite, ' \
                          '       c.steps, c.remark                                     ' \
                          '  from test_case c                                           ' \
                          ' inner join project p                                        ' \
                          '    on p.id = c.project_id                                   ' \
                          ' inner join test_case_node n                                       ' \
                          '    on n.id = c.node_id                                  ' \
                          ' where c.method = \'auto\'                                   ' \
                          '   and c.type = \'functional\'                               ' \
                          '   and p.name like \'%{project_name}%\'                     ' \
                          ' order by n.pos, c.num                                 '.format(
                project_name=self.case_keyword)
            logger.debug(sql_project)
            cur = db.cursor()
            cur.execute(sql_plan)
            if cur.rowcount == 0:
                logger.info('根据计划id找不到任何用例，尝试识别项目关键字')
                cur.execute(sql_project)
                if cur.rowcount == 0:
                    logger.error('无匹配用例')
                    sys.exit(1)
            col_names = [i[0] for i in cur.description]
            self.testcases = [dict(zip(col_names, row)) for row in cur]
            logger.info('从数据库读取到%s条用例' % len(self.testcases))
            cur.close()
        except Exception as ex:
            logger.cri('获取用例异常：%s' %self.case_keyword,ex)

    def generate_case(self):
        """
        根据用例生成用例脚本

        Returns:
        """

        if os.path.exists('TestCase'):
            shutil.rmtree('TestCase')
        os.mkdir('TestCase')
        os.chdir('TestCase')

        current_file = ''
        current_case = ''
        for xh, testcase in enumerate(self.testcases):
            case = {}
            case['case_num'] = testcase.get('case_num')
            case['pre_type'] = ''
            case['prerequisite'] = ''
            case['desc_type'] = ''
            case['desc'] = ''
            case['desc_data'] = ''
            case['result_type'] = ''
            case['result'] = ''
            case['result_data'] = ''

            # 解析出来的文件名
            filename = testcase.get('node_path').split('/')[-1]
            # 用例文件夹
            module = testcase.get('project_name') + testcase.get('node_path').replace(filename, '')

            # 用例id
            case_id = testcase.get('id')
            # 用例编号
            case_num = testcase.get('case_num')
            if not os.path.exists(module):
                os.makedirs(module)

            with open(os.path.join(module, 'test_' + str(filename) + '.py'), 'a+', encoding='utf-8') as classfile:
                # 新建类文件，一个明细模块一个类文件
                if current_file != filename:
                    current_file = filename
                    classfile.write('# coding=utf-8\r\n')
                    classfile.write('import sys\n')
                    classfile.write('import pytest,allure\n')
                    classfile.write('from tool import logger\n')
                    classfile.write('from paladin import Paladin\r\n')

                    # 类定义
                    # classfile.write('@pytest.mark.%s\n' % filename)  # 用于筛选测试用例
                    classfile.write('class Test_%s:\n' % filename)

                    # 执行前的操作
                    classfile.write('\tdef setup_class(self):\n')
                    classfile.write('\t\tself.paladin = Paladin(None)\n\n')

                # 一条用例一个方法
                # title格式 模块_编号_名称_caseid，约定，方便自动解析allure结果
                classfile.write(
                    '\t@allure.title(\'%s_%s_%s_%s\')\n' % (filename, case_num, testcase.get('name'), case_id))
                classfile.write('\tdef test_%s(self):\n' % case_num)

                steps = json.loads(testcase.get('steps'))

                for step in steps:
                    del (step['num'])
                    # 前置条件（每条用例只支持一个前置条件）

                    #解析变量，例如[sysdate]返回YYYY-MM-DD；[sysdate_scope]返回YYYY-MM-DD - YYYY-MM-DD
                    try:
                        if step['desc_data'][0]=='[' :
                            step['desc_data']=_get_variable(step['desc_data'])
                    except:
                        pass
                    try:
                        if step['result'][0]=='[':
                            step['result']=_get_variable(step['result'])
                    except:
                        pass

                    if current_case != case_num:
                        current_case = case_num
                        case['pre_type'] = testcase.get('pre_type') if testcase.get('pre_type') else ''
                        case['prerequisite'] = testcase.get('prerequisite') if testcase.get('prerequisite') else ''
                        if testcase.get('pre_type') == '自定义脚本':
                            classfile.write('\t\tlogger.info(\'执行前置自定义脚本\')\n')
                            classfile.write('%s\n' % _generate_script(testcase.get('prerequisite')))
                            case['pre_type'] = ''
                            case['prerequisite'] = ''
                    else:
                        case['pre_type'] = ''
                        case['prerequisite'] = ''
                        case['desc_type'] = ''
                        case['desc'] = ''
                        case['desc_data'] = ''
                        case['result_type'] = ''
                        case['result'] = ''

                    # 操作类型特殊处理
                    if step.get('desc_type') == '用例':  # 如果是用例调用其它用例，无需预期结果，直接返回：
                        for x in step.get('desc_type').replace('，', ',').split(','):
                            classfile.write('\t\t#执行其它用例：%s\n' % x)
                            classfile.write('\t\tself.test_%s()\n\n' % x)
                        continue
                    elif step.get('desc_type') == '自定义脚本':  # 如果是自定义脚本（自定义脚本每行前的tab占位符可以用空格来代替，写用例后要校验一下脚本能否编译通过）：
                        if step.get('result') is None or step.get(
                            'result') == '':  # 没有预期结果的一律当做true,需在do_action返回true或false
                            step['result'] = 1
                        case = dict(case, **step)
                        classfile.write('\t\tcase = %s\n' % str(case))
                        classfile.write('\t\tlogger.info(\'执行用例自定义脚本\')\n')
                        classfile.write('%s\n' % _generate_script(step.get('desc')))
                    else:
                        case = dict(case, **step)

                    # 检查类型特殊处理
                    if step.get('result_type') == '自定义脚本':  # 如果是自定义脚本（自定义脚本每行前的tab占位符可以用空格来代替，写用例后要校验一下脚本能否编译通过）：
                        classfile.write('\t\tlogger.info(\'执行检查自定义脚本\')\n')
                        classfile.write('%s\n\n' % _generate_script(step.get('result')))
                        continue

                    if step.get('result') is None or step.get(
                            'result') == '':  # 没有预期结果的一律当做true,需在do_action返回true或false
                        case['result'] = 1
                    elif '|' in str(step.get('result')):  # 预期结果格式：预期操作数据|预期结果，如select count(1) from table1|25
                        case['result_data'] = str(step.get('result')).split('|')[1]
                        case['result'] = str(step.get('result')).split('|')[0]
                    else:
                        case['result'] = step.get('result')
                    if case['desc_type'] != '自定义脚本' :
                        classfile.write('\t\tcase = %s\n' % str(case))
                        classfile.write('\t\tresult = self.paladin.do_action(case)\n')
                        if case['result_type'] != '表格某列的值':
                            if case['result_type'] == '数据库结果':
                                classfile.write(
                                    '\t\tassert result == int(case.get(\'result_data\')),\'实际结果[%s]不等于预期结果[%s]\'%(result,case.get(\'result_data\'))\n\n')
                            else:
                                classfile.write(
                                    '\t\tassert result == case.get(\'result\'),\'实际结果[%s]不等于预期结果[%s]\'%(result,case.get(\'result\'))\n\n')
                        else:
                            classfile.write(
                                '\t\tassert result == case.get(\'result_data\'),\'实际结果[%s]不等于预期结果[%s]\'%(result,case.get(\'result_data\'))\n\n')
                    if not self.check_case(case):
                        logger.error('用例编号【%s】检查不通过，请检查！' % case_num)
                        classfile.write('用例编写有误!')
                        sys.exit(1)

                if xh == len(self.testcases) - 1 or current_file != self.testcases[xh + 1].get('node_path').split('/')[
                    -1]:
                    classfile.write('\n\tdef teardown_class(self):\n')
                    classfile.write('\t\tself.paladin.exit()\n')

    def check_case(self, case):
        flag = 0

        # 前置操作
        if case['pre_type'] != '' and case['pre_type'] not in list(
                x.value for x in PreType):
            logger.error('前置类型有误！%s' % case['pre_type'])
            flag += 1
        if case['pre_type'] != '' and case['prerequisite'] == '':
            logger.error('前置类型不为空时，前置条件必填')
            flag += 1

        # 操作检查
        if case['desc_type'] == '' or case['desc_type'] not in list(
                x.value for x in Ele) + list(
            x.value for x in CaseType):
            logger.error('操作类型有误！%s' % case['desc_type'])
            flag += 1
        if case['desc'] == '':
            logger.error('操作步骤不能为空！')
            flag += 1
        if case['desc_type'] in (
                Ele.INPUT.value, Ele.RICHINPUT.value, Ele.SINGLEDROPDOWN.value, Ele.MULTIDROPDOWN.value,
                CaseType.LOGIN.value) and case[
            'desc_data'] == '':
            logger.error('操作类型为【%s】时操作数据不能为空！' % case['desc_type'])
            flag += 1

        # 检查
        if case['result_type'] != '' and case['result_type'] not in list(x.value for x in ExpectType):
            logger.error('检查类型有误！%s' % case['result_type'])
            flag += 1
        # if case['result_type'] in (
        #         ExpectType.DBDATASET.value, ExpectType.DATAGRID.value, ExpectType.DATAGRIDHAS.value,
        #         ExpectType.EMAILHAS.value, ExpectType.COLUMNVALUE.value,
        #         ExpectType.PAGEHAS.value,
        #         ExpectType.TAKESCREEN.value, ExpectType.ATTACHMENT.value, ExpectType.SCRIPT.value) and case[
        #     'result_data'] is None:
        #     logger.error('检查类型为【%s】时检查内容不能为空！' % case['result_type'])
        #     flag += 1
        if case['result_type'] in (
                ExpectType.DATAGRIDTOTAL.value, ExpectType.DATAGRIDCNT.value, ExpectType.COLUMNVALUE.value,
                ExpectType.MESSAGE.value) and case['result'] == '':
            logger.error('检查类型为【%s】时预期结果不能为空！' % case['result_type'])
            flag += 1
        return True if flag == 0 else False


if __name__ == '__main__':
    if len(sys.argv) == 2:
        ce = CaseGenerator(sys.argv[1])
        ce.generate_case()
        logger.info('生成[%s]的用例完成！' % sys.argv[1])
    else:
        logger.error('未传入计划id或项目名称！')
        sys.exit(1)
