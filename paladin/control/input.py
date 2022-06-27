# coding=utf-8
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tool import logger

from paladin.control.common import Common


class Input(Common):
    """
    普通输入/富文本输入组件
    """

    def __init__(self, browser, tag, index):
        super(Input, self).__init__(browser, tag, index)

    def _get_element(self):
        input = super(Input,self)._get_element('input.el-input__inner')
        if input is not None:
            logger.info('定位到普通文本框组件:' + str(self.tag))
            return input

        input = super(Input, self)._get_element('textarea')
        if input is not None:
            logger.info('定位到富文本框组件:' + str(self.tag))
            return input

        # divs = self.browser.find_elements(By.CSS_SELECTOR, 'div.el-form-item')
        # logger.debug('定位到el-form-item组件%s个' % len(divs))
        # elements = []
        # for div in divs:
        #     # 有些el-form-item下没有el-form-item__label，这种情况就不是标准组件，忽略
        #     try:
        #         label = self.browser.find_element(By.CSS_SELECTOR, 'label.el-form-item__label', div)
        #         if label.text == self.tag:
        #             ele = self.browser.find_element(By.CSS_SELECTOR, 'input.el-input__inner', div)
        #             logger.info('定位到普通文本框组件:' + str(self.tag))
        #             if not ele:
        #                 ele = self.browser.find_element(By.CSS_SELECTOR, 'textarea', div)
        #                 logger.info('定位到富文本框组件:' + str(self.tag))
        #             try:
        #                 label.click()  # 当页面出现多个元素，判断它是否可点击（不可见或被遮挡的一般不可点击）
        #                 if self.browser.find_element(By.CSS_SELECTOR, 'a', label):  # 如果label自身就是超链接，需关掉弹出窗口
        #                     from selenium.webdriver import ActionChains
        #                     ActionChains(self.browser.driver).send_keys(Keys.ESCAPE).perform()
        #                 elements.append(ele)
        #                 self.label = label
        #             except:
        #                 continue
        #     except:
        #         continue
        #
        # if len(elements) >= self.index:
        #     return elements[self.index - 1]