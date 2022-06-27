from selenium.webdriver.common.by import By

from paladin.control.common import Common
from tool import logger


class Checkbox(Common):
    """
    复选框组件
    """

    def __init__(self, browser, tag, index):
        super(Checkbox, self).__init__(browser, tag, index)

    def _get_element(self):
        checks = self.browser.find_elements(By.CSS_SELECTOR, 'label.el-checkbox')
        logger.debug('定位到el-checkbox组件%s个' % len(checks))
        for check in checks:
            # 有些勾选框没有checkbox__label的捕获异常，接着往下找
            try:
                if self.browser.find_element(By.CSS_SELECTOR, 'span.el-checkbox__label', check).text == self.tag:
                    return check
            except:
                continue

    def do(self, key=None):
        """
        勾选框的勾选操作

        Args:
            key: 是否勾选，值域：'1', '0', 1, 0, True, False

        Returns:
            bool:是否成功
        """
        assert key in ('1', '0', 1, 0, True, False), '勾选框输入值错误！1,0,True,False'
        checkbox = self.browser.find_element(By.CSS_SELECTOR, 'span.el-checkbox__input', self.element)
        nowchecked = 'is-checked' in checkbox.get_attribute('class')  # 如果当前选中状态
        if int(key) == 1:  # 勾
            if nowchecked:  # 当前处于勾选状态
                pass
            else:
                checkbox.click()
                logger.info('勾选:%s' % self.tag)
        else:  # 不勾
            if nowchecked:  # 当前处于勾选状态
                checkbox.click()
                logger.info('反选:%s' % self.tag)
            else:
                pass
        return True
