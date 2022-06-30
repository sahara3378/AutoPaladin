import time
from selenium.webdriver.common.by import By
from paladin.control.common import Common
from tool import logger


class DropdownSingle(Common):
    """
    下拉单选框
    """

    def __init__(self, browser, tag, index):
        super(DropdownSingle, self).__init__(browser, tag, index)

    def _get_element(self):
        return super(DropdownSingle, self)._get_element('div.el-select')

    def do(self, key=None):
        """
        下拉单选框选择操作

        Args:
            key:选择的项目（全匹配）

        Returns:
            bool:是否成功
        """
        try:
            self.element.click()
            time.sleep(1)
            dropdowns = self.browser.find_elements(By.CSS_SELECTOR, 'div.el-select-dropdown')
            for dropdown in dropdowns:
                if dropdown.is_displayed() and dropdown.is_enabled() and 'display: none' not in dropdown.get_attribute(
                        'style'):
                    try:
                        dropinput = self.browser.find_element(By.CSS_SELECTOR, 'input.el-input__inner', dropdown)
                        if dropinput:
                            self.browser.type(dropinput, key)
                        else:
                            dropinput = self.browser.find_element(By.CSS_SELECTOR, 'input.el-input__inner', self.element)
                            if dropinput:
                                self.browser.type(dropinput, key)
                    except:
                        pass
                    items = self.browser.find_elements(By.CSS_SELECTOR, 'li', dropdown)
                    for item in items:
                        if 'display: none' not in item.get_attribute('style') and key == item.text:
                            item.click()
                            logger.info('选择:%s' % key)
                            time.sleep(1)
                            return True
        except Exception as ex:
            logger.error('下拉框输入错误',ex)
            return False
