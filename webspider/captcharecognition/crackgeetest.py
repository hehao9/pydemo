import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = '347428365@qq.com'
PASSWORD = 'h3911160512'
BORDER = 6
INIT_LEFT = 60


class CrackGeetest():
    def __init__(self):
        self.url = 'https://www.geetest.com/show/'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.email = EMAIL
        self.password = PASSWORD

    def open(self):
        """
        打开网页输入用户名密码
        :return:
        """
        self.browser.get(self.url)
        tab = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tab-item-1')))
        tab.click()
        # email = self.wait.until(EC.presence_of_element_located((By.ID, 'email')))
        # password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        # email.send_keys(self.email)
        # password.send_keys(self.password)

    def get_geetest_button(self):
        """
        获取初始验证按钮
        :return: 按钮对象
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        return button

    def get_position(self):
        """
        获取验证图片位置
        :return: 验证图片元组
        """
        img = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
        time.sleep(2)
        location = img.location_once_scrolled_into_view
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return top, bottom, left, right

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_geetest_image(self, name='captcha.png'):
        """
        获取验证图片
        :param name:
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证图片位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        screenshot.save('screenshot.png')
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 去两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return: 缺口偏移量
        """
        left = INIT_LEFT
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阙值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 当前初速度
        v0 = 0
        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 1
            else:
                # 加速度为负5
                a = -4
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 当前速度
            v0 += a * t
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(x, 0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def login(self):
        """
        登录
        :return: None
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login-btn')))
        submit.click()
        time.sleep(10)
        print('登陆成功')

    def crack(self):
        # 输入用户名密码
        self.open()
        # 点击验证按钮
        button = self.get_geetest_button()
        button.click()
        # 向下滚动
        self.browser.execute_script('window.scroll(0, 500)')
        # 获取带缺口的验证图片
        image1 = self.get_geetest_image('captcha1.png')
        # 获取验证图片
        self.browser.execute_script('document.querySelectorAll("canvas")[2].style=""')
        time.sleep(1)
        image2 = self.get_geetest_image('captcha2.png')


        # 获取缺口位置
        gap = self.get_gap(image1, image2)
        print('缺口位置', gap)
        # 减去缺口位移
        gap -= BORDER
        # 获取移动轨迹
        track = self.get_track(gap)
        print('滑动轨迹', track)
        # 获取滑块
        slider = self.get_slider()
        # 拖动滑块
        self.move_to_gap(slider, track)
        try:
            success = self.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
            self.login()
        except TimeoutException:
            print('未通过验证，登陆失败')


if __name__ == '__main__':
    crack = CrackGeetest()
    crack.crack()