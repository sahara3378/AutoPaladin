from selenium.webdriver.common.by import By

from paladin.control.common import Common
from tool import logger


class Radiobox(Common):
    """
    单选框组件
    """

    def __init__(self, browser, tag, index):
        super(Radiobox, self).__init__(browser, tag, index)

    def _get_element(self):
        checks = self.browser.find_elements(By.CSS_SELECTOR, 'label.el-radio')
        logger.debug('定位到el-radio组件%s个' % len(checks))
        for check in checks:
            # 有些勾选框没有checkbox__label的捕获异常，接着往下找
            try:
                if self.browser.find_element(By.CSS_SELECTOR, 'span.el-radio__label', check).text == self.tag:
                    return check
            except:
                continue

    def do(self,arg=None):
        """
        单选框的勾选操作

        Returns:
            bool:是否成功
        """
        checkbox = self.browser.find_element(By.CSS_SELECTOR, 'span.el-radio__input', self.element)
        nowchecked = 'is-checked' in checkbox.get_attribute('class')  # 如果当前选中状态
        if nowchecked:  # 当前处于勾选状态
            logger.info('%s当前已处于选中状态' % self.tag)
            pass
        else:
            checkbox.click()
            logger.info('勾选:%s' % self.tag)
        return True
