import time

from selenium.webdriver.common.by import By

from paladin.control.common import Common
from tool import logger


class Notice(Common):
    """
    消息组件
    """

    def __init__(self, browser, tag, index):
        super(Notice, self).__init__(browser, tag, index)

    def _get_element(self):
        """
        消息框一般要在操作后经过一段等待时间才出来，所以获取异常时抛出warn信息
        :return:
        """
        try:
            element = self.browser.find_element(By.CSS_SELECTOR, 'div.el-notification__content')
            element2 = self.browser.find_element(By.CSS_SELECTOR, 'div.el-message')
            if element:
                logger.info('定位到消息框！')
                self.txt = element.text
                logger.info('消息内容：%s' % self.txt)
                try:
                    time.sleep(0.5)
                    close = self.browser.find_element(By.CSS_SELECTOR, 'div.el-notification__closeBtn.el-icon-close')
                    if close:
                        close.click()
                        logger.info('关闭消息框')
                except Exception as ex:
                    logger.warn('关闭消息框异常！',ex)
                return element
            elif element2:
                logger.info('定位到样式2的消息框！')
                self.txt = element2.text
                logger.info('消息内容：%s' % self.txt)
                time.sleep(3)
                return element2
        except Exception as ex:
            logger.warn('定位消息框异常！')
            logger.warn(ex)
            return None

    def message(self):
        """
        获取消息框的消息内容

        Returns:
            str:消息内容
        """
        return self.txt
