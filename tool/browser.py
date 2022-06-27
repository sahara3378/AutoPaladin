# coding=gbk
import os
import shutil
import sys
import time
import traceback
import platform

from selenium import webdriver
from selenium.webdriver import ActionChains, FirefoxProfile
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tool import logger, configs


class Browser:
    """
    封装了webdriver的一些常用方法，结合了logger；将浏览器的参数配置化
    """

    def __init__(self, type=None):
        logger.info('初始化浏览器...')
        self.atta_path = os.path.join(os.environ.get('AutoPaladin'), 'case', 'attachment')
        if os.path.exists(self.atta_path):
            shutil.rmtree(self.atta_path)
        os.makedirs(self.atta_path)
        logger.info('重建浏览器附件下载文件夹:%s' % self.atta_path)
        self.browsertype = type if type else configs.get_config('browser', 'type')
        if platform.system() == 'Windows':
            exesuf = '.exe'
        elif platform.system() == 'Linux':
            exesuf = ''
        else:
            logger.cri('不支持的操作系统类型:%s' % platform.system())
            sys.exit(1)
        if self.browsertype == 'chrome':
            try:
                os.system('taskkill /f /im chromedriver.exe')
                # os.system('taskkill /f /im chrome.exe')
            except:
                pass
            options = Options()
            prefs = {"download.default_directory": self.atta_path}
            options.add_experimental_option("prefs", prefs)
            if platform.system() == 'Linux':
                options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(
                executable_path=os.path.join(os.environ.get('AutoPaladin'), 'resource', 'chromedriver' + exesuf),
                options=options)
            logger.info('使用谷歌浏览器')
            logger.info('修改谷歌浏览器默认文件下载路径：%s' % self.atta_path)
        elif self.browsertype == 'firefox':
            try:
                os.system('taskkill /f /im geckodriver.exe')
                # os.system('taskkill /f /im firefox.exe')
            except:
                pass
            firefox_profile = configs.get_config('browser', 'firefox_profile')
            if firefox_profile and os.path.exists(firefox_profile):
                logger.info('火狐浏览器指定用户配置:%s' % firefox_profile)
                profile = FirefoxProfile(firefox_profile)
            else:
                logger.info('火狐浏览器未指定或找不到用户配置，使用默认用户配置')
                profile = None
            self.driver = webdriver.Firefox(
                executable_path=os.path.join(os.environ.get('AutoPaladin'), 'resource', 'geckodriver' + exesuf),
                service_log_path=os.path.join(os.environ.get('AutoPaladin'), 'log', 'firefox.log'),
                firefox_profile=profile)
            logger.info('使用火狐浏览器')
        elif self.browsertype == 'ie':
            if platform.system() != 'Windows':
                logger.cri('非Windows操作系统不支持IE浏览器')
                sys.exit(1)
            try:
                os.system('taskkill /f /im IEDriverServer.exe')
                # os.system('taskkill /f /im iexplore.exe')
            except:
                pass
            # 注意64位系统需采用32位的iedriver，否则会出现输入慢的现象
            self.driver = webdriver.Ie(os.path.join(os.environ.get('AutoPaladin'), 'resource', 'IEDriverServer.exe'))
            logger.info('使用IE浏览器')
        else:
            logger.cri('不支持的浏览器类型:%s' % self.browsertype)
            sys.exit(1)
        if self.driver:
            self.driver.maximize_window()

    def get(self, url):
        """访问浏览器地址

        Args:
            url:访问地址
        """
        if self.driver and url:
            self.driver.get(url)
            logger.info('打开网址：%s ' % url)

    def quit(self):
        """
        退出浏览器
        """
        if self.driver:
            logger.info('正在退出浏览器...')
            self.driver.quit()

    def refresh(self):
        """
        刷新浏览器
        """
        if self.driver:
            logger.info('刷新浏览器.')
            self.switch(None)
            self.driver.refresh()

    def switch(self, frame=None):
        """
        切换到frame

        Args:
            frame:frame，当为None时切换到默认窗口，即driver.switch_to.default_content

        Returns:
            bool:是否成功
        """
        if self.driver:
            if frame:
                try:
                    logger.debug('浏览器切换frame...')
                    self.driver.switch_to.frame(frame)
                    return True
                except Exception as ex:
                    logger.error('浏览器切换frame出现异常！')
                    logger.error(ex)
                    traceback.print_stack()
                    return False
            else:
                logger.debug('浏览器切换到默认窗口...')
                self.driver.switch_to.default_content()
                return True

    def execute_script(self, script, args=None):
        """
        执行javascript脚本

        Args:
            script: 脚本
            args: 参数

        Returns:
            bool:是否成功
        """
        try:
            self.driver.execute_script(script, args)
            logger.debug('浏览器执行脚本：%s' % script)
            return True
        except Exception as ex:
            logger.error('浏览器执行脚本异常！%s' % script)
            logger.error(ex)
            traceback.print_stack()
            return False

    def find_element(self, locator_type, locator_key, parent_element=None):
        """
        封装了webdriver的find_element_by_id、find_element_by_name等方法，获取WebElement

        Args:
            locator_type: 参考By
            locator_key: 定位路径
            parent_element:父级获取WebElement，如果有有值，则从该父级下获取，提高效率

        Returns:
            WebElement:元素

        """
        if parent_element:
            logger.debug('从父级元素开始查找...%s' % str(parent_element))
        try:
            if locator_type == By.ID:
                return parent_element.find_element_by_id(
                    locator_key) if parent_element else self.driver.find_element_by_id(
                    locator_key)
            elif locator_type == By.NAME:
                return parent_element.find_element_by_name(
                    locator_key) if parent_element else self.driver.find_element_by_name(
                    locator_key)
            elif locator_type == By.XPATH:
                return parent_element.find_element_by_xpath(
                    locator_key) if parent_element else self.driver.find_element_by_xpath(
                    locator_key)
            elif locator_type == By.LINK_TEXT:
                return parent_element.find_element_by_link_text(
                    locator_key) if parent_element else self.driver.find_element_by_link_text(
                    locator_key)
            elif locator_type == By.PARTIAL_LINK_TEXT:
                return parent_element.find_element_by_partial_link_text(
                    locator_key) if parent_element else self.driver.find_element_by_partial_link_text(
                    locator_key)
            elif locator_type == By.TAG_NAME:
                return parent_element.find_element_by_tag_name(
                    locator_key) if parent_element else self.driver.find_element_by_tag_name(
                    locator_key)
            elif locator_type == By.CLASS_NAME:
                return parent_element.find_element_by_class_name(
                    locator_key) if parent_element else self.driver.find_element_by_class_name(
                    locator_key)
            elif locator_type == By.CSS_SELECTOR:
                return parent_element.find_element_by_css_selector(
                    locator_key) if parent_element else self.driver.find_element_by_css_selector(
                    locator_key)
            else:
                logger.error('不支持的定位类型')
                return None
        except Exception as ex:
            logger.error('定位元素出现异常：%s-->--%s' % (locator_type, locator_key))
            logger.error(ex)
            return None

    def find_elements(self, locator_type, locator_key, parent_element=None):
        """
        见find_element

        Args:
            locator_type:
            locator_key:
            parent_element:

        Returns:
            List[WebElement]:元素列表
        """
        if parent_element:
            logger.debug('从父级元素开始查找...%s' % str(parent_element))
        try:
            if locator_type == By.ID:
                return parent_element.find_elements_by_id(
                    locator_key) if parent_element else self.driver.find_elements_by_id(
                    locator_key)
            elif locator_type == By.NAME:
                return parent_element.find_elements_by_name(
                    locator_key) if parent_element else self.driver.find_elements_by_name(
                    locator_key)
            elif locator_type == By.XPATH:
                return parent_element.find_elements_by_xpath(
                    locator_key) if parent_element else self.driver.find_elements_by_xpath(
                    locator_key)
            elif locator_type == By.LINK_TEXT:
                return parent_element.find_elements_by_link_text(
                    locator_key) if parent_element else self.driver.find_elements_by_link_text(
                    locator_key)
            elif locator_type == By.PARTIAL_LINK_TEXT:
                return parent_element.find_elements_by_partial_link_text(
                    locator_key) if parent_element else self.driver.find_elements_by_partial_link_text(
                    locator_key)
            elif locator_type == By.TAG_NAME:
                return parent_element.find_elements_by_tag_name(
                    locator_key) if parent_element else self.driver.find_elements_by_tag_name(
                    locator_key)
            elif locator_type == By.CLASS_NAME:
                return parent_element.find_elements_by_class_name(
                    locator_key) if parent_element else self.driver.find_elements_by_class_name(
                    locator_key)
            elif locator_type == By.CSS_SELECTOR:
                return parent_element.find_elements_by_css_selector(
                    locator_key) if parent_element else self.driver.find_elements_by_css_selector(
                    locator_key)
            else:
                logger.error('不支持的定位类型')
                return None
        except Exception as ex:
            logger.error('定位元素出现异常：%s-->--%s' % (locator_type, locator_key))
            logger.error(ex)
            return None

    def type(self, element, word):
        """
        元素输入操作

        Args:
            element:WebElement
            word:输入值

        Returns:
            bool:是否成功
        """
        try:
            if self.browsertype == 'ie':
                for w in word:
                    element.send_keys(w)
                    time.sleep(0.01)
            else:
                element.send_keys(word)
            logger.info('浏览器输入：%s' % word)
            return True
        except Exception as ex:
            logger.error('浏览器输入异常：%s' % word)
            logger.error(ex)
            traceback.print_stack()
            return False

    def click(self, element):
        """
        点击元素

        Args:
            element:WebElement

        Returns:
            bool:是否成功
        """
        try:
            element.click()
            logger.info('浏览器点击：%s' % element)
            return True
        except Exception as ex:
            logger.error('浏览器点击：%s异常！' % element)
            logger.error(ex)
            traceback.print_stack()
            return False

    def double_click(self, element):
        """
        双击元素

        Args:
            element: WebElement元素

        Returns:
            bool:是否成功
        """
        try:
            action_chains = ActionChains(self.driver)
            action_chains.double_click(element).perform()
            logger.info('浏览器双击：%s' % element)
            return True
        except Exception as ex:
            logger.error('浏览器双击：%s异常！' % element)
            logger.error(ex)
            traceback.print_stack()
            return False

    def wait_for_element(self, locator_type, locator_key, time=20):
        """
        等待元素出现

        Args:
            locator_type: 参考Selenium的By
            locator_key:定位路径
            time:超时时间，秒

        Returns:
            WebElement:元素
        """
        try:
            element = WebDriverWait(self.driver, time).until(
                # presence_of_element_located
                EC.visibility_of_element_located((locator_type, locator_key))
            )
            return element
        except Exception as ex:
            logger.error('Error waiting for element:%s %s after %s seconds' % (locator_type, locator_key, time))
            logger.error(ex)
            traceback.print_stack()

    def wait_for_elements(self, locator_type, locator_key, time=20):
        """
        等待元素出现

        Args:
            locator_type: 参考Selenium的By
            locator_key:定位路径
            time:超时时间，秒

        Returns:
            List[WebElement]:元素列表
        """
        try:
            elements = WebDriverWait(self.driver, time).until(
                # presence_of_element_located
                EC.visibility_of_all_elements_located((locator_type, locator_key))
            )
            return elements
        except Exception as ex:
            logger.error('Error waiting for elements:%s %s after %s seconds' % (locator_type, locator_key, time))
            logger.error(ex)
            traceback.print_stack()

    def wait_for_element_to_click(self, locator_type, locator_key, time=30):
        """
        等待元素出现可点击

        Args:
            locator_type:参考Selenium的By
            locator_key:定位路径
            time:超时时间，秒

        Returns:
            WebElement:元素
        """
        try:
            element = WebDriverWait(self.driver, time).until(
                EC.element_to_be_clickable((locator_type, locator_key))
            )
            return element
        except Exception as ex:
            logger.error(
                'Error waiting for element to click:%s %s after %s seconds' % (locator_type, locator_key, time))
            logger.error(ex)
            traceback.print_stack()

    def take_screenshot(self, name):
        """
        截图操作，图片存储:case/pics/YYYYMMDD/[文件名]_时间戳.png

        Args:
            name:文件名

        Returns:
            str,str:图片文件绝对路径,文件名
        """
        try:
            root = os.path.join(os.environ.get('AutoPaladin'), 'case', 'pics')
            f_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            f_date = f_time[:8]
            f_date_p = os.path.join(root, f_date)
            file_name = '%s_%s.png' % (name, f_time)
            picture_url = os.path.join(f_date_p, file_name)
            if not os.path.exists(f_date_p):
                os.mkdir(f_date_p)
            self.driver.get_screenshot_as_file(picture_url)
            logger.info("截图保存成功：%s" % picture_url)
            # self.generate_pic(root)
            return picture_url, file_name
        except Exception as ex:
            logger.error('截图出现异常！%s' % picture_url)
            logger.error(ex)
            traceback.print_stack()
            return False

    def generate_pic(self, root):
        pic_html = os.path.join(root, 'pics.html')
        with open(pic_html, 'w', encoding='gbk') as f1:
            dates = os.listdir(root)
            dates.sort(reverse=True)
            for fdate in dates:
                if os.path.isdir(os.path.join(root, fdate)):
                    f1.write('<p><b>%s</b></p>\n' % fdate)
                    pics = os.listdir(os.path.join(root, fdate))
                    pics.sort(reverse=True)
                    for pic in pics:
                        f1.write('<li><a href="%s\\%s">%s</a><br/></li>\n' % (fdate, pic, pic))
