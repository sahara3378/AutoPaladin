import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from tool import logger


class Common:
    """
    组件基类;
    tag: 组件的名称，如输入框“股票名称”，按钮“查询”等;如果为“-”,则表示不指定名字、所有满足的组件
    index:当页面出现多个名称一样的组件，获取第index个（注意，不可点击、隐藏的组件不包含在可选组件里）
    """

    def __init__(self, browser, tag, index=1):
        self.browser = browser
        self.tag = tag
        self.index = index
        self.element = WebElement(None, None)
        self.element = self._get_element()

    def has_element(self):
        """
        判断标准组件是否获取到了WebElement元素，获取不到元素则做不了任何动作

        Returns:
            bool:是否包含
        """
        return True if self.element else False

    def _get_element(self, type='input.el-input__inner'):
        """
        获取帕拉丁组件的WebElement
        标准组件为label+input，根据label的text定位
        """
        elements = []
        if self.tag == None or self.tag == '':
            logger.error('普通组件未指定标签！')
            return False
        elif self.tag == '-':
            logger.warn('普通组件未指定标签,将找到所有符合条件的组件！')
            elements = self.browser.find_elements(By.CSS_SELECTOR, type)
            logger.debug('定位到el-form-item组件%s个' % len(elements))
        else:
            divs = self.browser.find_elements(By.CSS_SELECTOR, 'div.el-form-item')
            logger.debug('定位到el-form-item组件%s个' % len(divs))
            
            for div in divs:
                # 有些el-form-item下没有el-form-item__label，这种情况就不是标准组件，忽略
                label = None
                try:
                    label = self.browser.find_element(By.CSS_SELECTOR, 'label.el-form-item__label', div)
                except:
                    pass
                if label is None:
                    continue
                else:
                    if label.text == self.tag:
                        # 如果有些组件名称相同（例如查询条件有，新增页面也有），都要存，根据传入的index判断取哪个
                        ele = self.browser.find_element(By.CSS_SELECTOR, type, div)
                        try:
                            label.click()  # 当页面出现多个元素，判断它是否可点击（不可见或被遮挡的一般不可点击）
                            if self.browser.find_element(By.CSS_SELECTOR, 'a', label):  # 如果label自身就是超链接，需关掉弹出窗口
                                ActionChains(self.browser.driver).send_keys(Keys.ESCAPE).perform()
                            elements.append(ele)
                            logger.info('定位到普通组件:' + str(self.tag))
                            self.label = label
                        except:
                            pass

        if len(elements) >= self.index:
            return elements[self.index - 1]

    def do(self, key=None):
        """
        标准组件的输入、勾选、执行、点击等动作。

        Args:
            key:输入类组件需要操作的内容。按钮类组件可传可不传；输入类必须传值；勾选类传入0/1或True/False；表格类详见DataGrid

        Returns:
            bool:是否成功
        """
        if self.element:
            try:
                self.element.click()
                logger.info('点击：' + str(self.tag))
                if key:
                    self.element.send_keys(Keys.CONTROL, 'a')
                    self.element.send_keys(Keys.BACKSPACE)
                    self.browser.type(self.element, key)
                    if '日期' in self.get_attribute('placeholder'):
                        # 针对日期组件，输入值后需按下回车日期值才能赋上，并且要按下Esc键把日期组件缩起
                        self.element.send_keys(Keys.ENTER)
                        self.element.send_keys(Keys.ESCAPE)
                        time.sleep(0.1)
                    logger.info(str(self.tag) + ' 输入：' + str(key))
                return True
            except Exception as ex:
                logger.error('组件操作异常！',ex)
                return False
        return False

    def get_attribute(self, attribute):
        """
        获取组件的WebElement元素的属性值

        Args:
            attribute:属性名，如text、class等

        Returns:
            str:属性值
        """
        if self.element:
            try:
                if attribute == 'text':
                    result = self.element.text
                else:
                    result = self.element.get_attribute(attribute)
                return result
            except Exception as ex:
                logger.error('获取组件属性异常！%s' % attribute,ex)
                return None
