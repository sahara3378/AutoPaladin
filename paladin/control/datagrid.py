import time
import traceback
import re

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from paladin.control.common import Common
from tool import logger, configs


class DataGrid(Common):
    """
    表格组件
    """

    def __init__(self, browser, tag, index):
        super(DataGrid, self).__init__(browser, tag, index)

    def _get_element(self):
        try:
            tables = self.browser.find_elements(By.CSS_SELECTOR, 'div.el-table')
            rts = []
            for table in tables:
                if table.is_displayed() and table.is_enabled():
                    rts.append(table)
            if len(rts) >= self.index:
                return rts[self.index - 1]
        except Exception as ex:
            logger.error('找不到grid组件')
            logger.error(ex)
            traceback.print_stack()

    def total(self):
        """
        获取表格的总计数（即表格下方的“共x条”）

        Returns:
            int:记录条数
        """
        try:
            cnt = self.browser.find_element(By.CSS_SELECTOR, '.el-pagination__total').text.replace('共', '').replace('条',
                                                                                                                    '').replace(
                ' ', '')
            logger.info('列表计数:%s' % cnt)
            return int(cnt)
        except Exception as ex:
            logger.error('计数错误')
            logger.error(ex)
            traceback.print_stack()

    def __check_i(self, checkbox):
        if checkbox:
            nowchecked = 'is-checked' in checkbox.get_attribute('class')  # 如果当前选中状态
            if not nowchecked:
                try:
                    if checkbox.is_displayed() and checkbox.is_enabled():
                        checkbox.click()
                    else:
                        self.browser.execute_script("arguments[0].click();",
                                                    checkbox)  # 有些弹出窗口的列表勾选框点不了，但是用javascript可以执行
                    logger.info('勾选表格')
                    return True
                except Exception as ex:
                    logger.error('勾选表格出现异常！')
                    logger.error(ex)
                    traceback.print_stack()
            else:
                logger.info('表格已处于勾选状态')
        else:
            logger.error('表格无勾选框')
        return False

    def check(self, all=True, key_words=[], row_index=[]):
        """
        对于带多选功能的表格，提供勾选功能

        Args:
            all: 是否全选，默认True；True时为全选，且key_words、row_index参数无效
            key_words: all=False才生效。行内容包含关键字则勾选，如['公司信息','机构信息']
            row_index: all=False才生效。需要勾选的行，下标从1开始，如[1,2],[2,5,9]

        Returns:
            bool:是否成功
        """
        if self.has_element():
            if all:
                try:
                    time.sleep(1)
                    head = self.browser.find_element(By.CSS_SELECTOR, 'div.el-table__header-wrapper', self.element)
                    if head:
                        check = self.browser.find_element(By.CSS_SELECTOR, 'span.el-checkbox__input', head)
                        return self.__check_i(check)
                except Exception as ex:
                    logger.error('全选表格出现异常！')
                    logger.error(ex)
                    traceback.print_stack()
            else:
                try:
                    content = self.browser.find_element(By.CSS_SELECTOR, 'div.el-table__body-wrapper', self.element)
                    if content:
                        trs = self.browser.find_elements(By.CSS_SELECTOR, 'tr.el-table__row', content)
                        for x in range(len(trs)):
                            check = self.browser.find_element(By.CSS_SELECTOR, 'span.el-checkbox__input',
                                                              trs[x])
                            for key_word in key_words:  # 按关键字匹配
                                if key_word in trs[x].text:
                                    self.__check_i(check)
                            if x + 1 in row_index:  # 按行号匹配
                                self.__check_i(check)
                        return True
                except Exception as ex:
                    logger.error('勾选表格出现异常！')
                    logger.error(ex)
                    traceback.print_stack()
                    return False

    def rowcount(self):
        """
        获取表格的记录行数（即表格下方无多少行时手动计算行数）

        Returns:
            int:记录条数
        """
        return len(self.data())

    def data(self, title=None, index=1):
        """
        获取列表的内容（包含表头）；或者列表指定列的内容

        Args:
            title:列头
            index:下标从1开始，不传默认取第一行

        Returns:
            表格全内容：list[dict1,dict2]:表格内容,例如[{'股票代码':'000001','股票名称':'平安银行'},{'股票代码':'000002','股票名称':'万科A'}]
            表格某列内容：str

        Examples:
            print(d.data(title='用户名称'))
            print(d.data(title='用户名称',index=2))

        """
        try:
            logger.info('正在获取表格数据...')
            data = []
            headers = self.browser.find_elements(By.CSS_SELECTOR, 'tr>th>div', self.element)
            head = list(i.text for i in headers)

            exclude_head = configs.get_config('case', 'exclude_cols').replace('，', ',').split(',')
            logger.info('根据sys.cfg配置文件exclude_cols参数排除读取列:%s' % str(exclude_head))

            rows = self.browser.find_elements(By.CSS_SELECTOR,
                                              '.el-table__body-wrapper>.el-table__body>tbody>.el-table__row',
                                              self.element)
            for row in rows:
                cells = list(i.text for i in self.browser.find_elements(By.CSS_SELECTOR, 'td>div', row))
                d = dict(zip(head, cells))
                for col in exclude_head:
                    if col in d.keys():
                        del (d[col])
                if '' in d.keys():  # 列头为空，不获取该单元格
                    del (d[''])
                data.append(d)
            logger.debug('列表数据:%s' % data)
            if title:
                return str(data[index - 1][title])
            else:
                return data
        except Exception as ex:
            logger.error('获取列表数据异常！')
            logger.error(ex)
            traceback.print_stack()


    def has(self, key_word):
        """
        判断表格内容是否包含给定关键字

        Args:
            key_word: 关键字;注意,所给关键字和单元格内容全匹配

        Returns:
            bool:是否包含
        """
        result = self.data()
        content = []

        for r in result:
            content.extend(list(r.values()))

        logger.info('从[%s]中检索关键字[%s]...' % (str(content), key_word))
        return True if key_word in content else False

    '''
    判断指定行的某一列的内容是否是指定的值
    '''
    def column(self,columnName):
        """
        @param columnName: 列名,行号，如果只有列名则行号默认为1
        @param key_word: 列值
        @return:
            object:查询到结果
        """
        cln = columnName.split(',')
        if len(cln)==2:
            args=(cln[0],int(cln[1]))
        else:
            args=cln[0]
        result1 = self.data(*args)


        logger.info('查询到的列值:%s' % result1)

        if result1 is not None:
            return result1
        else:
            return False



    def do(self, operation, key_word=None, row_index=1):
        """
        根据行号或行内容关键字，点击表格的某行或操作按钮

        Args:
            row_index: 行数，下标从1开始
            key_word: 行内容任意一列包含的关键字
            operation: “点击”、“勾选”，或表格操作列按钮的中文名称

        Returns:
            bool:是否成功
        """
        rows = self.browser.find_elements(By.CSS_SELECTOR,
                                          '.el-table__body-wrapper>.el-table__body>tbody>tr', self.element)

        if key_word is not None:
            for i in range(len(rows)):
                if str(key_word) == '0' or key_word in rows[i].text:
                    if operation == '点击':
                        self.browser.find_elements(By.CSS_SELECTOR, 'td', rows[i])[1].click()
                        logger.info('根据所给关键字\"%s\"点击表格第%s行' % (key_word, i + 1))
                        return True
                    elif operation == '勾选':
                        if str(key_word) == '0':
                            return self.check(all=True)
                        else:
                            return self.check(all=False, key_words=[key_word, ])
                    else:
                        logger.info('%s 执行操作：%s' % (key_word, operation))
                        return self._row_opration(rows[i], operation)

        elif str(row_index).isdigit():
            if len(rows) >= row_index:
                try:
                    if operation == '点击':
                        self.browser.find_elements(By.CSS_SELECTOR, 'td', rows[row_index - 1])[1].click()
                        logger.info('点击表格第%s行' % row_index)
                        return True
                    elif operation == '勾选':
                        if str(row_index) == '0':
                            return self.check(all=True)
                        else:
                            return self.check(all=False, row_index=[row_index, ])
                    else:
                        logger.info('第%s行执行操作：%s' % (row_index, operation))
                        return self._row_opration(rows[row_index - 1], operation)
                except Exception as ex:
                    logger.error('表格第%s行%s操作异常！' % (row_index, operation))
                    logger.error(ex)
                    traceback.print_stack()
            else:
                logger.error('指定的行数row_index错误！')
        else:
            logger.error('row_index、key_word必须正确指定！')

        return False

    def _row_opration(self, row, operation):
        ops = self.browser.find_elements(By.CSS_SELECTOR, 'td>div.cell>button', row)  # 操作列中的按钮
        logger.debug('定位到%s个操作按钮' % len(ops))

        for op in ops:
            location_x = op.location['x']
            self.browser.execute_script('arguments[0].scrollIntoView();', op)
            if op.location['x'] != location_x:  # 如果scrollIntoView后x坐标发生偏移，则代表表格有横向滚动条
                self.browser.find_elements(By.CSS_SELECTOR, 'td', row)[1].click()
                for i in range(500):
                    ActionChains(self.browser.driver).send_keys(Keys.ARROW_RIGHT).perform()
                    time.sleep(0.3)
                    location_x_new = op.location['x']
                    if location_x_new == location_x:  # 如果本次右移后x坐标不变，表示滚动条已经拉到最右边
                        break
                    location_x = location_x_new

            ActionChains(self.browser.driver).move_to_element(op).perform()
            time.sleep(1)

            poppers = self.browser.find_elements(By.CSS_SELECTOR, 'div.el-tooltip__popper.is-light')
            innerHTML = poppers[-1].get_attribute('innerHTML')  # 最后一个popper为最近一次悬浮显示出来的
            innerHTML = re.sub('<.*>', '', innerHTML)
            if operation == innerHTML:
                action_chains = ActionChains(self.browser.driver)
                action_chains.reset_actions()
                action_chains.click(op).perform()
                action_chains.reset_actions()
                return True
            else:
                continue
            # for popper in poppers:
            #     # innerHTML = popper.get_attribute('innerHTML')
            #     # innerHTML = re.sub('<.*>', '', innerHTML)
            #     # logger.debug('popper text %s' % innerHTML)
            #     if not 'display: none' in popper.get_attribute('style'):  # 找到显示状态的popper，根据文字判断该按钮是什么操作
            #         if operation == popper.text:
            #             action_chains = ActionChains(self.browser.driver)
            #             action_chains.reset_actions()
            #             action_chains.click(op).perform()
            #             action_chains.reset_actions()
            #
            #             return True

        linkops = self.browser.find_elements(By.CSS_SELECTOR, 'a.el-tooltip', row)  # 操作列中的超链接
        for linkop in linkops:
            if operation == linkop.get_attribute("text"):
                action_chains = ActionChains(self.browser.driver)
                action_chains.move_to_element(linkop).perform()
                time.sleep(0.1)
                action_chains.click(linkop).perform()
                action_chains.reset_actions()
                logger.info('点击操作列按钮：%s %s' % (operation, str(row)))
                return True

        return False
