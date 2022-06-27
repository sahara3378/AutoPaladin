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
    ��װ��webdriver��һЩ���÷����������logger����������Ĳ������û�
    """

    def __init__(self, type=None):
        logger.info('��ʼ�������...')
        self.atta_path = os.path.join(os.environ.get('AutoPaladin'), 'case', 'attachment')
        if os.path.exists(self.atta_path):
            shutil.rmtree(self.atta_path)
        os.makedirs(self.atta_path)
        logger.info('�ؽ���������������ļ���:%s' % self.atta_path)
        self.browsertype = type if type else configs.get_config('browser', 'type')
        if platform.system() == 'Windows':
            exesuf = '.exe'
        elif platform.system() == 'Linux':
            exesuf = ''
        else:
            logger.cri('��֧�ֵĲ���ϵͳ����:%s' % platform.system())
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
            logger.info('ʹ�ùȸ������')
            logger.info('�޸Ĺȸ������Ĭ���ļ�����·����%s' % self.atta_path)
        elif self.browsertype == 'firefox':
            try:
                os.system('taskkill /f /im geckodriver.exe')
                # os.system('taskkill /f /im firefox.exe')
            except:
                pass
            firefox_profile = configs.get_config('browser', 'firefox_profile')
            if firefox_profile and os.path.exists(firefox_profile):
                logger.info('��������ָ���û�����:%s' % firefox_profile)
                profile = FirefoxProfile(firefox_profile)
            else:
                logger.info('��������δָ�����Ҳ����û����ã�ʹ��Ĭ���û�����')
                profile = None
            self.driver = webdriver.Firefox(
                executable_path=os.path.join(os.environ.get('AutoPaladin'), 'resource', 'geckodriver' + exesuf),
                service_log_path=os.path.join(os.environ.get('AutoPaladin'), 'log', 'firefox.log'),
                firefox_profile=profile)
            logger.info('ʹ�û�������')
        elif self.browsertype == 'ie':
            if platform.system() != 'Windows':
                logger.cri('��Windows����ϵͳ��֧��IE�����')
                sys.exit(1)
            try:
                os.system('taskkill /f /im IEDriverServer.exe')
                # os.system('taskkill /f /im iexplore.exe')
            except:
                pass
            # ע��64λϵͳ�����32λ��iedriver����������������������
            self.driver = webdriver.Ie(os.path.join(os.environ.get('AutoPaladin'), 'resource', 'IEDriverServer.exe'))
            logger.info('ʹ��IE�����')
        else:
            logger.cri('��֧�ֵ����������:%s' % self.browsertype)
            sys.exit(1)
        if self.driver:
            self.driver.maximize_window()

    def get(self, url):
        """�����������ַ

        Args:
            url:���ʵ�ַ
        """
        if self.driver and url:
            self.driver.get(url)
            logger.info('����ַ��%s ' % url)

    def quit(self):
        """
        �˳������
        """
        if self.driver:
            logger.info('�����˳������...')
            self.driver.quit()

    def refresh(self):
        """
        ˢ�������
        """
        if self.driver:
            logger.info('ˢ�������.')
            self.switch(None)
            self.driver.refresh()

    def switch(self, frame=None):
        """
        �л���frame

        Args:
            frame:frame����ΪNoneʱ�л���Ĭ�ϴ��ڣ���driver.switch_to.default_content

        Returns:
            bool:�Ƿ�ɹ�
        """
        if self.driver:
            if frame:
                try:
                    logger.debug('������л�frame...')
                    self.driver.switch_to.frame(frame)
                    return True
                except Exception as ex:
                    logger.error('������л�frame�����쳣��')
                    logger.error(ex)
                    traceback.print_stack()
                    return False
            else:
                logger.debug('������л���Ĭ�ϴ���...')
                self.driver.switch_to.default_content()
                return True

    def execute_script(self, script, args=None):
        """
        ִ��javascript�ű�

        Args:
            script: �ű�
            args: ����

        Returns:
            bool:�Ƿ�ɹ�
        """
        try:
            self.driver.execute_script(script, args)
            logger.debug('�����ִ�нű���%s' % script)
            return True
        except Exception as ex:
            logger.error('�����ִ�нű��쳣��%s' % script)
            logger.error(ex)
            traceback.print_stack()
            return False

    def find_element(self, locator_type, locator_key, parent_element=None):
        """
        ��װ��webdriver��find_element_by_id��find_element_by_name�ȷ�������ȡWebElement

        Args:
            locator_type: �ο�By
            locator_key: ��λ·��
            parent_element:������ȡWebElement���������ֵ����Ӹø����»�ȡ�����Ч��

        Returns:
            WebElement:Ԫ��

        """
        if parent_element:
            logger.debug('�Ӹ���Ԫ�ؿ�ʼ����...%s' % str(parent_element))
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
                logger.error('��֧�ֵĶ�λ����')
                return None
        except Exception as ex:
            logger.error('��λԪ�س����쳣��%s-->--%s' % (locator_type, locator_key))
            logger.error(ex)
            return None

    def find_elements(self, locator_type, locator_key, parent_element=None):
        """
        ��find_element

        Args:
            locator_type:
            locator_key:
            parent_element:

        Returns:
            List[WebElement]:Ԫ���б�
        """
        if parent_element:
            logger.debug('�Ӹ���Ԫ�ؿ�ʼ����...%s' % str(parent_element))
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
                logger.error('��֧�ֵĶ�λ����')
                return None
        except Exception as ex:
            logger.error('��λԪ�س����쳣��%s-->--%s' % (locator_type, locator_key))
            logger.error(ex)
            return None

    def type(self, element, word):
        """
        Ԫ���������

        Args:
            element:WebElement
            word:����ֵ

        Returns:
            bool:�Ƿ�ɹ�
        """
        try:
            if self.browsertype == 'ie':
                for w in word:
                    element.send_keys(w)
                    time.sleep(0.01)
            else:
                element.send_keys(word)
            logger.info('��������룺%s' % word)
            return True
        except Exception as ex:
            logger.error('����������쳣��%s' % word)
            logger.error(ex)
            traceback.print_stack()
            return False

    def click(self, element):
        """
        ���Ԫ��

        Args:
            element:WebElement

        Returns:
            bool:�Ƿ�ɹ�
        """
        try:
            element.click()
            logger.info('����������%s' % element)
            return True
        except Exception as ex:
            logger.error('����������%s�쳣��' % element)
            logger.error(ex)
            traceback.print_stack()
            return False

    def double_click(self, element):
        """
        ˫��Ԫ��

        Args:
            element: WebElementԪ��

        Returns:
            bool:�Ƿ�ɹ�
        """
        try:
            action_chains = ActionChains(self.driver)
            action_chains.double_click(element).perform()
            logger.info('�����˫����%s' % element)
            return True
        except Exception as ex:
            logger.error('�����˫����%s�쳣��' % element)
            logger.error(ex)
            traceback.print_stack()
            return False

    def wait_for_element(self, locator_type, locator_key, time=20):
        """
        �ȴ�Ԫ�س���

        Args:
            locator_type: �ο�Selenium��By
            locator_key:��λ·��
            time:��ʱʱ�䣬��

        Returns:
            WebElement:Ԫ��
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
        �ȴ�Ԫ�س���

        Args:
            locator_type: �ο�Selenium��By
            locator_key:��λ·��
            time:��ʱʱ�䣬��

        Returns:
            List[WebElement]:Ԫ���б�
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
        �ȴ�Ԫ�س��ֿɵ��

        Args:
            locator_type:�ο�Selenium��By
            locator_key:��λ·��
            time:��ʱʱ�䣬��

        Returns:
            WebElement:Ԫ��
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
        ��ͼ������ͼƬ�洢:case/pics/YYYYMMDD/[�ļ���]_ʱ���.png

        Args:
            name:�ļ���

        Returns:
            str,str:ͼƬ�ļ�����·��,�ļ���
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
            logger.info("��ͼ����ɹ���%s" % picture_url)
            # self.generate_pic(root)
            return picture_url, file_name
        except Exception as ex:
            logger.error('��ͼ�����쳣��%s' % picture_url)
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
