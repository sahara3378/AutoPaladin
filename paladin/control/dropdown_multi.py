import time
import traceback
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from paladin.control.common import Common
from tool import logger


class DropdownMulti(Common):
    """
    下拉多选框
    """

    def __init__(self, browser, tag, index):
        super(DropdownMulti, self).__init__(browser, tag, index)

    def _get_element(self):
        return super(DropdownMulti, self)._get_element('div.el-select')

    def do(self, key=None):
        """
        下拉多选框的多选操作

        Args:
            key:选择的项目，全匹配

        Returns:
            True，False

        Examples:
            p.find_control_paladin(Ele.MULTIDROPDOWN, '资产组合').do('[111111]xxxxx1,[222222]xxxxx2')
            p.find_control_paladin(Ele.MULTIDROPDOWN, '用户名称').do('测试用户')
        """
        key = str(key)
        try:
            self.element.click()  # 先把下拉框加载出来
            time.sleep(2)
            dropdowns = self.browser.find_elements(By.CSS_SELECTOR, 'div.el-select-dropdown')
            for dropdown in dropdowns:
                if dropdown.is_displayed() and dropdown.is_enabled() and 'display: none' not in dropdown.get_attribute(
                        'style'):
                    try:  # 可输入关键字过滤的下拉多选框
                        input = self.browser.find_element(By.CSS_SELECTOR, 'input.el-input__inner', dropdown)
                        input.send_keys(Keys.ARROW_DOWN)
                        if ',' in key or '，' in key:
                            key = key.replace('，', ',').split(',')
                            # type(key) == list or type(key) == tuple:
                            for k in key:
                                input.send_keys(Keys.CONTROL, 'a')
                                input.send_keys(Keys.BACKSPACE)
                                self.browser.type(input, k)
                                input.send_keys(Keys.ENTER)
                        else:
                            self.browser.type(input, key)
                            input.send_keys(Keys.ENTER)
                    except:  # 只可选择不可输入过滤的下拉多选框
                        dds = self.browser.find_elements(By.CSS_SELECTOR, 'ul>li>label', dropdown)
                        for x in range(len(dds)):
                            if dds[x].text in key:
                                dds[x].click()

                    time.sleep(1)
                    self.element.click()
                    # self.label.click()  # 将下拉框缩起来
                    # if self.browser.find_element(By.CSS_SELECTOR, 'a', self.label):  # 如果label自身就是超链接，需关掉弹出窗口
                    #     ActionChains(self.browser.driver).send_keys(Keys.ESCAPE).perform()
                    logger.info('选择%s' % key)
                    time.sleep(1)
                    return True
            return False

        except Exception as ex:
            logger.error('下拉多选框输入错误')
            logger.error(ex)
            traceback.print_stack()
            return False
