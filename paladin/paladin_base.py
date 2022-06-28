import os
import sys
import time
import re
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from paladin.control import *
from paladin.type import *
from tool import *
from tool import Browser
import allure


class Paladin:
    def __init__(self, url, name=None, pwd=None, browser=None):
        """
        打开帕拉丁的网址，并登录（可选）

        Args:
            url: 帕拉丁访问地址
            name: 用户名
            pwd: 密码
            browser: 浏览器，不指定则使用配置文件，支持的类型：chrome、firefox、ie、edge
        """
        self.start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        logger.info('当前时间%s' % self.start_time)
        self.browser = Browser(browser)
        self.browser.get(url)
        self.iframe = None
        if name and pwd:
            self.login(name, pwd)

    def login(self, name, pwd, url=None):
        """
        登录帕拉丁系统，根据页面判断若当前已登录，则先登出再登录

        Args:
            name: 用户名
            pwd: 密码
            url: 登录地址（可选），给定url时先跳转

        Returns:
            bool:是否成功

        """

        if configs.get_config('db', 'type') == 'oracle':
            db = ''
        else:
            db = configs.get_config('mysql', 'saas_user') + '.'
        r = dbms.query('SELECT SUM(CNT)'
                       '  FROM (SELECT COUNT(1) CNT'
                       '           FROM {db}TUSER'
                       '          WHERE NAME = \'{name}\''
                       '            AND (THEME_STYLE <> 2 OR UNFOLD_DEF <> 1)'
                       '         UNION ALL'
                       '         SELECT COUNT(1) CNT'
                       '           FROM {db}T_USER_PARAMETER P'
                       '           JOIN {db}TUSER U'
                       '             ON P.USERID = U.ID'
                       '          WHERE U.NAME = \'{name}\''
                       '            AND P.PARAMETER_VALUE = \'Y\') T'.format(name=name, db=db))
        if r > 0:
            logger.cri('帕拉丁登录失败！请设置用户[%s]个性化菜单为：系统菜单风格-经典；左侧菜单栏默认状态-展开；菜单默认展开-全部为否' % name)
            sys.exit(1)

        if url:
            self.browser.get(url)
        try:
            try:
                logo = self.browser.find_element(By.CSS_SELECTOR, 'div.login_logo')  # 如果不是在登录页面，需要先注销
                if not logo:
                    self.logout()
            except:
                pass

            nameinput = self.browser.find_element(By.ID, 'name')
            pwdinput = self.browser.find_element(By.ID, 'pwd')
            self.browser.type(nameinput, name)
            self.browser.type(pwdinput, pwd)
            self.browser.type(pwdinput, Keys.ENTER)

            if self.browser.wait_for_element(By.CSS_SELECTOR, 'div.sc-usermenu', time=40):
                logger.info('帕拉丁登录成功！')
                return True
            else:
                logger.cri('帕拉丁登录失败！')
                return False
        except Exception as ex:
            logger.error('登录出现异常！')
            logger.error(ex)
            traceback.print_stack()
            return False

    def logout(self):
        """
        退出登录

        Returns:
            bool:是否成功

        """
        try:
            self.browser.switch(None)
            u = self.browser.find_element(By.CSS_SELECTOR, 'div.sc-usermenu')
            u.click()
            lis = u.find_elements(By.CSS_SELECTOR,'ul>li>a')
            for li in lis:
                time.sleep(0.5)
                if self.browser.find_element(By.CSS_SELECTOR, 'span', li).text == '退出登录':
                    li.click()
                    break

            if self.browser.wait_for_element(By.ID, 'name'):
                logger.info('注销成功！')
                return True

            return False
        except Exception as ex:
            logger.error('注销出现异常！')
            logger.error(ex)
            traceback.print_stack()
            return False

    def exit(self):
        """
        关闭浏览器
        Returns:

        """
        self.browser.quit()

    def open(self, menu):
        """
        打开帕拉丁菜单，最多支持三级菜单；
        注意，用户的菜单模式：统菜单风格-经典；左侧菜单栏默认状态-展开；菜单默认展开-否

        Args:
            menu:菜单名称，如 【 平台管理应用-法人管理 】、【 基本管理功能-报表权限管理[表格字段权限] 】

        Returns:
            bool:是否成功
       """
        try:
            self.browser.refresh()
            self.browser.wait_for_element(By.CSS_SELECTOR, 'div.menu_label.el-tooltip.level1')
            marrays = menu.split('-')
            assert len(marrays) in (2, 3), '菜单格式错误'

            # 如果存在tab页
            tab = None
            if '[' in marrays[-1]:
                tab = marrays[-1].split('[')[1].replace(']', '')
                logger.info('tab页：%s' % tab)
                marrays[-1] = marrays[-1].split('[')[0]

            menus1 = self.browser.find_elements(By.CSS_SELECTOR, 'div.menu_label.el-tooltip.level1')
            for menu1 in menus1:
                if (menu1.text == marrays[0]):
                    menu1.click()
                    logger.info('一级菜单：' + str(marrays[0]))
                    time.sleep(0.5)
                    menus2 = self.browser.find_elements(By.CSS_SELECTOR, 'div.menu_label.el-tooltip.level2')
                    for menu2 in menus2:
                        if (menu2.text == marrays[1]):
                            menu2.click()
                            logger.info('二级菜单：' + str(marrays[1]))
                            break
                    break

            if len(marrays) == 3:
                time.sleep(0.5)
                menus3 = self.browser.find_elements(By.CSS_SELECTOR, 'div.menu_label.el-tooltip.level3')
                for menu3 in menus3:
                    if (menu3.text == marrays[2]):
                        logger.info('打开三级菜单：' + str(menu))
                        menu3.click()
                        break
            else:
                logger.info('打开二级菜单：' + str(menu))

            time.sleep(0.5)
            self.switch_tab(tab)
            time.sleep(0.5)
            return True
        except Exception as ex:
            logger.error('打开菜单出现异常：%s' % menu)
            logger.error(ex)
            traceback.print_stack()
            return False

    def switch_menu(self, menuname):
        """
        切换菜单

        Args:
            menuname:菜单名称

        Returns:
            bool:是否成功

        """
        self._switch_frame(False)
        menus = self.browser.find_elements(By.CSS_SELECTOR, 'li.sc-tab>a>span.label')
        for menu in menus:
            if menu.text == menuname:
                logger.info('切换菜单：%s' % menuname)
                self.browser.click(menu)
                return True

    def close_menu(self, menuname):
        """
        关闭菜单

        Args:
            menuname: 菜单名称

        Returns:
            bool:是否成功

        """
        self._switch_frame(False)
        try:
            menus = self.browser.find_elements(By.CSS_SELECTOR, 'li.sc-tab>a')
            for menu in menus:
                if self.browser.find_element(By.CSS_SELECTOR, 'span.label', menu).text == menuname:
                    self.browser.find_element(By.CSS_SELECTOR, 'span.close', menu).click()
                    logger.info('关闭菜单：%s' % menuname)
                    return True
        except Exception as ex:
            logger.error('关闭菜单出现异常！')
            logger.error(ex)
            traceback.print_stack()
            return False

    def click_treenode(self, treenode):
        """
        点击树形目录

        Args：
            treenode: 树形目录名称

        Returns:
            bool:是否成功

        """
        try:
            self.browser.wait_for_element(By.CSS_SELECTOR, 'span.el-tree-node__label')
            tree = treenode.split('-')
            for i in range(len(tree)):
                trns = self.browser.find_elements(By.CSS_SELECTOR, 'span.el-tree-node__label')
                for trn in trns:
                    if (trn.text == tree[i]):
                        trn.click()
                        logger.info(str(i + 1) + '级tree：' + str(tree[i]))
                        time.sleep(0.5)

            time.sleep(0.5)
            return True
        except Exception as ex:
            logger.error('打开树形目录出现异常：%s' % treenode)
            logger.error(ex)
            traceback.print_stack()
            return False

    def close_dial(self):
        """
        关闭弹出窗口

        Returns:
            bool:是否成功

        """
        try:
            closes = self.browser.find_elements(By.CSS_SELECTOR, 'i.el-dialog__close')
            for close in closes:
                if close.is_displayed():
                    close.click()
                    logger.info('关闭弹窗')
                    return True
            return False
        except Exception as ex:
            logger.error('关闭弹窗发生异常！')
            logger.error(ex)
            traceback.print_stack()
            return False

    def switch_tab(self, tabname=None):
        """
        切换菜单的子tab页

        Args:
            tabname:子tab页名称

        Returns:
            bool:是否成功

        """
        self._switch_frame()
        if tabname:
            self._switch_frame(False)
            frames = self.browser.find_elements(By.CSS_SELECTOR, 'iframe')
            for frame in frames:
                if frame.is_displayed():
                    logger.debug('Iframe src:%s' % frame.get_attribute('src'))
                    self.browser.switch(frame)
                    break
            tabs = self.browser.find_elements(By.CSS_SELECTOR, 'div.el_tab')
            for tab in tabs:
                if tab.text == tabname:
                    logger.info('切换菜单tab页：%s' % tabname)
                    self.browser.click(tab)
                    self._switch_frame()
                    return True
        else:
            return True
        logger.error('切换菜单tab页错误：%s' % tabname)
        return False

    def _switch_frame(self, default=True):
        """
        切换frame
        """
        self.browser.switch(None)
        if not default:
            return

        # 循环切入到最子级的iframe，在当前iframe下再也找不到子iframe时返回
        while True:
            frames = self.browser.find_elements(By.CSS_SELECTOR, 'iframe')
            # iframe可见才操作
            # iframe的src无url时不切换，例如saas：基本管理功能-邮件发送管理[邮件模板设置]
            # 排除特殊的预览PDF页面，例如场外：指令文件模版管理
            frames = [frame for frame in frames if frame.is_displayed() and 'http' in frame.get_attribute(
                'src') and not 'pdfFrame' == frame.get_attribute('id')]
            if len(frames) == 0:
                break
            for frame in frames:
                try:
                    self.iframe = frame.get_attribute('src')
                    logger.debug('Iframe src:%s' % self.iframe)
                    self.browser.switch(frame)
                except:
                    logger.error('Error occurred while trying to switch iframe!')
                    pass

    def page_has(self, keyword, label='div'):
        """
        判断页面上指定标签中是否包含所给关键字

        Args:
            keyword:关键字
            label:标签名，默认div，使用CSS_SELECTOR定位

        Returns:
            bool:是否成功

        """
        if keyword is None or keyword.replace(' ', '') == '':
            logger.error('未给定关键字')
            return None
        self._switch_frame()
        divs = self.browser.find_elements(By.CSS_SELECTOR, label)
        has = False
        for div in divs:
            if div.is_displayed():
                if keyword in div.text.replace(' ', '') or keyword in div.get_attribute('innerHTML'):
                    logger.info('页面查找到关键字:%s' % keyword)
                    logger.debug('[text] %s' % div.text)
                    logger.debug('[innerHTML] %s' % div.get_attribute('innerHTML'))
                    has = True
        return has

    def find(self, type, tag='', index=1, retries=0, interval=0):
        """
        根据组件类型、组件名，查找帕拉丁标准组件
        会尝试多次定位组件，有时候页面会出现加载效果，定位不到，需等待加载完后再尝试定位

        Args:
            type:组件类型，详见type.Ele
            tag:标签名；部分组件可不用传入，例如表格
            index:页面出现相同标签名时，获取第几个，默认第一个，下标从1开始
            retries:重试次数，如果没传值，默认取配置文件参数ele_loc_retries
            interval:重试间隔，单位：秒。如果没传值，默认取配置文件参数ele_loc_interval

        Returns:
            Common:帕拉丁标准组件

        Examples:
            paladin.find_control(Ele.INPUT, '股票代码').do('688878')
            paladin.find_control(Ele.DATAGRID).do(operation='勾选',row_index=1)
        """
        time.sleep(0.5)
        # 重试次数
        if str(retries).isdigit() and retries > 0:
            ele_loc_retries = int(retries)
        else:
            ele_loc_retries = int(configs.get_config('browser', 'ele_loc_retries'))

        # 重试间隔
        if str(interval).isdigit() and interval > 0:
            ele_loc_interval = int(interval)
        else:
            ele_loc_interval = int(configs.get_config('browser', 'ele_loc_interval'))

        for i in range(ele_loc_retries):
            if i > 0:
                logger.debug('重新获取获取帕拉丁组件...[%s]...[%s]...第[%s]次' % (type, tag, i + 1))
            control = self._find_i(type, tag, index)
            if control.has_element():
                return control
            if i == ele_loc_retries - 1:
                logger.error('%s次尝试定位失败！' % ele_loc_retries)
                return None
            time.sleep(ele_loc_interval)

    def _find_i(self, type, tag='', index=1):
        self._switch_frame()
        if type == Ele.BUTTON:
            return Button(self.browser, tag, index)
        elif type == Ele.LINKBUTTON:
            return LinkButton(self.browser, tag, index)
        elif type == Ele.INPUT:
            return Input(self.browser, tag, index)
        elif type == Ele.CHECKBOX:
            return Checkbox(self.browser, tag, index)
        elif type == Ele.RADIOBOX:
            return Radiobox(self.browser, tag, index)
        elif type == Ele.SINGLEDROPDOWN:
            return DropdownSingle(self.browser, tag, index)
        elif type == Ele.MULTIDROPDOWN:
            return DropdownMulti(self.browser, tag, index)
        elif type == Ele.NOTICE:
            return Notice(self.browser, tag, index)
        elif type == Ele.DATAGRID:
            return DataGrid(self.browser, tag, index)
        elif type == Ele.CUSTOM:
            return Custom(self.browser, tag, index)

    def upload(self, filename):
        """
        帕拉丁的标准上传页面，上传文件(如果不是标准页面，需另外写上传方法）

        Args:
            filename:文件的绝对路径

        Returns:
            bool:是否成功
        """
        if not os.path.exists(filename):
            logger.error('上传的文件不存在！%s' % filename)
            return False
        self.browser.type(self.browser.find_element(By.NAME, 'file'), filename)
        try:
            file = self.browser.find_element(By.CSS_SELECTOR, 'a.el-upload-list__item-name')
            logger.error('上传文件：%s' % filename)
            if file:
                if file.text in filename:
                    return True
            return False
        except Exception as ex:
            logger.error('上传文件错误')
            logger.error(ex)
            traceback.print_stack()
            return False

    def do_action(self, case):
        """
        给测试用例脚本调用；
        执行前置条件；
        操作类型、操作步骤 转换为 组件类型、组件名称；
        最后根据检查类型获取执行结果

        Args:
            case:从测试用例文件的读取的用例行内容，如 {'用例编号': 'IPO_ZB_10001', '名称': '登录', '前置类型': None, '前置条件': None, '操作类型': '登录', '操作步骤': 'http://192.168.72.96:8999/scxx-web/paladin', '操作数据': 'sah/1', '检查类型': None, '检查内容': None, '预期结果': 1, '备注': None}

        Returns:
            object:实际执行结果;如果无预期结果，默认返回bool，否则根据检查类型获取实际结果值
        """
        logger.info('do_action 内容：%s' % case)
        # case_bh = case['用例编号']
        # pre_type = case['前置类型']
        # pre_con = case['前置条件']
        # case_type = case['操作类型']
        # case_path = case['操作步骤']
        # case_data = case['操作数据']
        # case_check_type = case['检查类型']
        # case_check_content = case['检查内容']
        # logger.info('检查内容的值为：%s' % case_check_content)
        # case_check_expect = case['预期结果']
        case_bh = case['case_num']
        pre_type = case['pre_type']
        pre_con = case['prerequisite']
        case_type = case['desc_type']
        case_path = case['desc']
        case_data = case['desc_data']
        case_check_type = case['result_type']
        case_check_content = case['result']
        # case_check_expect = case['result']

        # Step1.执行前置条件
        if pre_type:
            logger.info('前置条件类型：%s' % pre_type)
            if not self.do_pre(pre_type, pre_con):
                logger.error('前置条件执行错误！')
                return False

        # Step2.执行操作步骤
        assert case_type in list(map(lambda c: c.value, Ele)) + list(map(lambda c: c.value, CaseType))
        for t in Ele:
            if case_type == t.value:
                case_type = t
                break
        for t in CaseType:
            if case_type == t.value:
                case_type = t
                break
        if case_type == CaseType.LOGIN:  # 登录
            assert '/' in case_data, '用户密码格式错误，形如admin/1'
            result = self.login(case_data.split('/')[0].replace(' ', ''), case_data.split('/')[1].replace(' ', ''),
                                case_path)
        elif case_type == CaseType.MENU:  # 打开菜单
            result = self.open(case_path)
        elif case_type == CaseType.TREENODE:  # 点击树形控件
            result = self.click_treenode(case_path)
        elif case_type == CaseType.SWITCHMENU:  # 切换菜单
            result = self.switch_menu(case_path)
        elif case_type == CaseType.SWITCHTAB:  # 切换TAB
            result = self.switch_tab(case_path)
        elif case_type == CaseType.CLOSEMENU:  # 关闭菜单
            result = self.close_menu(case_path)
        elif case_type == CaseType.CLOSEDIAL:  # 关闭弹窗
            result = self.close_dial()
        elif case_type == CaseType.WAIT:  # 等待
            logger.info('用例设置等待.等待时长%s秒' % case_path)
            time.sleep(int(case_path))
            result = True
        elif case_type == CaseType.UPLOAD:  # 上传文件
            result = self.upload(case_path)
        elif case_type == CaseType.READIPO:  # 读取IPO文件
            case_path_split = case_path.split(',')
            # 600078,XJ_SH,Z:\600078初步询价明细数据1589949462157.xls
            if len(case_path_split) == 3:
                result = osw.execute_ipo_tool(case_path_split[0], case_path_split[1], case_path_split[2])
            else:
                result = osw.execute_ipo_tool_cus(case_path)
        elif case_type == CaseType.SCRIPT:  # 自定义脚本
            result = 1
        else:  # 帕拉丁标准组件操作
            logger.info('---------------------paladin standard action %s begin---------------------' % case_bh)
            # 如果出现多个名称一样的元素，指定了某个，如"股票代码[2]" ；
            # 注意，下标从1开始
            index = 1
            try:
                if re.search(r'\[\d\]', case_path):
                    index = int(re.search(r'\d', case_path).group())
                    case_path = re.sub(r'\[\d\]', '', case_path)
            except:
                pass

            try:
                control = self.find(case_type, case_path, index)
                if control:
                    if isinstance(control, DataGrid):  # 表格操作
                        result = control.do(operation=case_path, key_word=case_data)
                    else:
                        result = control.do(case_data)
                else:
                    logger.info('获取组件为空:%s' % case_path)
                    result = False
            except Exception as ex:
                logger.error('Action 【%s】 执行发生异常！' % case_bh)
                logger.error(ex)
                traceback.print_stack()
                result = False

        # Step3.获取预期结果。支持的类型见AssertType
        if case_check_type:
            logger.info('检查类型:%s' % case_check_type)
            result = self.get_expect(case_check_type, case_check_content)

        logger.info('action执行结果:%s' % result)
        if not result or configs.get_config('case', 'take_screenshot_success') == '1':  # 用例action执行不通过或参数开启时截图
            ppath, pname = self.browser.take_screenshot(case_bh)
            allure.attach.file(ppath, pname, allure.attachment_type.PNG)
            allure.attach(body=r'<a href="{url}" target="_blank">{url}</a>'.format(url=self.iframe), name='错误地址',
                          attachment_type=allure.attachment_type.HTML)
        logger.info('---------------------paladin standard action %s end---------------------' % case_bh)

        return result

    def do_pre(self, type, contidion):
        """
        执行前置动作

        Args:
            type:前置类型参考PreType
            contidion:执行前置动作的内容

        Returns:
            object:根据前置类型获取实际结果值
        """
        for t in PreType:
            if type == t.value:
                type = t
                break
        if type == PreType.UPDATEDB:
            return dbms.update(contidion)
        elif type == PreType.EXECPROC:
            assert '|' in contidion, '格式错误：存储过程名|参数'
            return dbms.execproc(contidion.split('|')[0], contidion.split('|')[1])
        elif type == PreType.DELFILE:
            assert contidion != '', '文件名不能为空'
            return dbms.del_mongo_file(contidion)
        elif type == PreType.CMD:
            return osw.execute_cmd(contidion)
        elif type == PreType.UPDATECONFIG:
            try:
                for con in contidion.split('\n'):
                    # db.type=oracle
                    section = con.split('=')[0].split('.')[0]
                    key = con.split('=')[0].split('.')[1]
                    value = con.split('=')[1]
                    configs.set_config(section, key, value)
                return True
            except:
                return False
        else:
            return False

    def get_expect(self, type, content=None):
        """
        获取预期结果

        Args:
            type: 实际结果类型参考EcpectType
            content: 有些获取需要传参数，如数据库查询，需传sql

        Returns:
            object:根据检查类型获取实际结果值
        """
        for t in ExpectType:
            if type == t.value:
                type = t
                break
        if type == ExpectType.MESSAGE:
            # 有些功能要很久才操作完给出消息提示，这种可以在用例的"检查内容"指定最大重试次数(重试的间隔秒数仍然从配置文件拿)
            return self.find(Ele.NOTICE, retries=int(content) if content is not None and content.isdigit() else 0).message()
        elif type == ExpectType.DATAGRIDCNT:
            return str(self.find(Ele.DATAGRID).rowcount())
        elif type == ExpectType.DATAGRIDTOTAL:
            return str(self.find(Ele.DATAGRID).total())
        elif type == ExpectType.DATAGRID:
            return self.find(Ele.DATAGRID).data()
        elif type == ExpectType.DATAGRIDHAS:
            return content if self.find(Ele.DATAGRID).has(content) else ''
        # 表格某列的值（content:列名,行号  expect:预期结果）
        elif type == ExpectType.COLUMNVALUE:
            # return 0
            # Todo
            return self.find(Ele.DATAGRID).column(content)
        elif type == ExpectType.EMAILHAS:
            # Paladin初始化时会记录一个执行时间start_time，和该时间比较，如果这个时间后有查询到相关的邮件代表是本次自动化测试触发的邮件（不够严谨，待优化）
            # 建议自动化测试放在夜间执行，减少人工操作干扰
            return content if emailp.has_email(content, from_time=self.start_time) else ''
        elif type == ExpectType.PAGEHAS:
            return content if self.page_has(content) else ''
        elif type == ExpectType.PAGEHASNOT:
            return content if not self.page_has(content) else ''
        elif type == ExpectType.DBDATASET:
            return dbms.query(content)
        elif type == ExpectType.TAKESCREEN:
            ppath, pname = self.browser.take_screenshot(content)
            allure.attach.file(ppath, pname, allure.attachment_type.PNG)
            return content if ppath and pname else ''
        elif type == ExpectType.ATTACHMENT:
            file = os.path.join(self.browser.atta_path, content)
            if os.path.exists(file):
                for t in allure.attachment_type:
                    if t.value[1].upper() in content.upper():  # 判断附件后缀在不在allure支持的附件类型中
                        allure.attach.file(file, content, t)
                        return content
                logger.warn('附件已下载，但其格式不支持添加到allure报告中:%s' % file)
                return content
            else:
                logger.error('附件不存在:%s' % file)
                return ''
        else:
            return '不支持的预期结果类型！'
