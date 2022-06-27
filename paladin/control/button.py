import time

from selenium.webdriver.common.by import By

from paladin.control.common import Common
from tool import logger


class Button(Common):
    """
    普通按钮组件
    """

    def __init__(self, browser, tag, index=1):
        super(Button, self).__init__(browser, tag, index)

    def _get_element(self):
        try:
            btns = []
            buttons = self.browser.find_elements(By.CSS_SELECTOR, 'button.el-button')
            logger.debug('定位到%s个按钮组件' % len(buttons))
            for button in buttons:
                # Logger.debug('按钮文字:%s' % button.text)
                if button.text.replace(' ', '') == self.tag:
                    logger.info('定位到按钮组件:%s' % str(self.tag))
                    btns.append(button)
            return btns
        except Exception as ex:
            logger.error('定位按钮:%s异常' % self.tag)
            logger.error(ex)
            return False

    def do(self, key=None):
        if self.element:
            for b in self.element:
                try:
                    b.click()
                    time.sleep(1)
                    logger.info('点击按钮:%s' % self.tag)
                    return True
                except Exception as ex:
                    logger.warn('按钮点击异常:%s' % self.tag)
                    logger.warn(ex)
                    continue
            return False
        else:
            logger.error('找不到按钮:%s，无法点击！' % self.tag)
            return False
