import traceback

from selenium.webdriver.common.by import By
from paladin.control.common import Common
from tool import logger


class LinkButton(Common):
    """
    超链接按钮组件
    """

    def __init__(self, browser, tag, index):
        super(LinkButton, self).__init__(browser, tag, index)

    def _get_element(self):
        try:
            linkbtn = self.browser.find_element(By.PARTIAL_LINK_TEXT, self.tag)
            logger.info('定位到超链接:%s' % self.tag)
            return linkbtn
        except Exception as ex:
            logger.error('定位超链接错误:%s' % self.tag)
            logger.error(ex)
            traceback.print_stack()
            return None
