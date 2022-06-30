# coding=utf-8
from selenium.webdriver.common.by import By

from paladin.control.common import Common
from tool import logger


class Custom(Common):
    """
    自定义组件，tag传入CSS_SELECTOR或XPATH定位元素值
    """

    def __init__(self, browser, tag, index):
        super(Custom, self).__init__(browser, tag, index)

    def _get_element(self):
        try:
            if '//' in self.tag:
                eles = self.browser.find_elements(By.XPATH, self.tag)
            else:
                eles = self.browser.find_elements(By.CSS_SELECTOR, self.tag)
            if eles and len(eles) >= self.index:
                ele = eles[self.index - 1]
                if ele.is_displayed() and ele.is_enabled():
                    logger.info('定位到自定义元素：%s' % self.tag)
                    return ele
        except Exception as ex:
            logger.error('定位自定义元素出现异常！',ex)
