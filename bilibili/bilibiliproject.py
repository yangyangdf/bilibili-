# -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:19:32 2019
@author: xinyu
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

from PIL import Image

web = 'http://literallycanvas.com/'


# 初始化
def init():
    # 定义为全局变量，方便其他模块使用
    global url, browser, username, password, wait
    # 登录界面的url
    url = 'https://passport.bilibili.com/login'
    # 实例化一个chrome浏览器
    browser = webdriver.Chrome()
    # 用户名
    username = '***********'
    # 密码
    password = '***********'
    # 设置等待超时
    wait = WebDriverWait(browser, 20)


# 登录
def login():
    # 打开登录页面
    browser.get(url)
    # 获取用户名输入框
    user = wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
    # 获取密码输入框
    passwd = wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
    # 输入用户名
    user.send_keys(username)
    # 输入密码
    passwd.send_keys(password)

    # 获取登录按钮
    login_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.btn.btn-login')))
    # 随机延时点击
    time.sleep(random.random() * 3)
    login_btn.click()


# 设置元素可见
def show_element(element):
    browser.execute_script("arguments[0].style=arguments[1]", element, "display: block;")


# 设置元素不可见
def hide_element(element):
    browser.execute_script("arguments[0].style=arguments[1]", element, "display: none;")


# 对某元素截图
def save_pic(obj, name):
    try:
        pic_url = browser.save_screenshot('.\\bilibili.png')
        print("%s:截图成功!" % pic_url)

        # 获取元素位置信息
        left = obj.location['x']+153
        top = obj.location['y']+70
        right = left + obj.size['width'] + 54
        bottom = top + obj.size['height'] + 35

        print('图：' + name)
        print('Left %s' % left)
        print('Top %s' % top)
        print('Right %s' % right)
        print('Bottom %s' % bottom)
        print('')

        im = Image.open('.\\bilibili.png')
        im = im.crop((left, top, right, bottom))  # 元素裁剪
        file_name = 'bili_' + name + '.png'
        im.save(file_name)  # 元素截图
    except BaseException as msg:
        print("%s:截图失败!" % msg)


def cut():
    c_background = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas.geetest_canvas_bg.geetest_absolute')))
    c_slice = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas.geetest_canvas_slice.geetest_absolute')))
    c_full_bg = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas.geetest_canvas_fullbg.geetest_fade.geetest_absolute')))
    hide_element(c_slice)
    save_pic(c_background, 'back')
    show_element(c_slice)
    save_pic(c_slice, 'slice')
    show_element(c_full_bg)
    save_pic(c_full_bg, 'full')


# 判断像素是否相同
def is_pixel_equal(bg_image, fullbg_image, x, y):
    """
    :param bg_image: (Image)缺口图片
    :param fullbg_image: (Image)完整图片
    :param x: (Int)位置x
    :param y: (Int)位置y
    :return: (Boolean)像素是否相同
    """

    # 获取缺口图片的像素点(按照RGB格式)
    bg_pixel = bg_image.load()[x, y]
    # 获取完整图片的像素点(按照RGB格式)
    fullbg_pixel = fullbg_image.load()[x, y]

    # 设置一个判定值，像素值之差超过判定值则认为该像素不相同
    threshold = 70
    # 判断像素的各个颜色之差，abs()用于取绝对值
    if abs(bg_pixel[0] - fullbg_pixel[0] < threshold and bg_pixel[1] - fullbg_pixel[1] < threshold and
            bg_pixel[2] - fullbg_pixel[2] < threshold):
        # 如果差值在判断值之内，返回是相同像素

        return True

    else:
        # 如果差值在判断值之外，返回不是相同像素
        return False


# 计算滑块移动距离
def get_distance(bg_image, fullbg_image):
    '''
    :param bg_image: (Image)缺口图片
    :param fullbg_image: (Image)完整图片
    :return: (Int)缺口离滑块的距离
    '''

    # 滑块的初始位置
    distance = 60
    # 遍历像素点横坐标
    for i in range(distance, fullbg_image.size[0]):

        # 遍历像素点纵坐标
        for j in range(fullbg_image.size[1]):

            # 如果不是相同像素
            if not is_pixel_equal(fullbg_image, bg_image, i, j):
                # 返回此时横轴坐标就是滑块需要移动的距离

                return round(i*0.75)


# 构造滑动轨迹
def get_trace(distance):
    '''
    :param distance: (Int)缺口离滑块的距离
    :return: (List)移动轨迹
    '''

    # 创建存放轨迹信息的列表
    trace = []
    # 设置加速的距离
    faster_distance = distance * (3 / 5)
    # 设置初始位置、初始速度、时间间隔
    start, v0, t = 0, 0, 0.3
    # 当尚未移动到终点时
    while start < distance:
        # 如果处于加速阶段
        if start < round(faster_distance):
            # 设置加速度为2
            a = 2
        # 如果处于减速阶段
        else:
            # 设置加速度为-3
            a = -3
        # 移动的距离公式
        move = v0 * t + 1/2 * a * t * t
        # 此刻速度
        v = v0 + a * t
        # 重置初速度
        v0 = v
        # 重置起点
        start += move
        # 将移动的距离加入轨迹列表
        trace.append(round(move))

    # 返回轨迹信息
    return trace



# 模拟拖动
def move_to_gap(trace):
    # 得到滑块标签
    # slider = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gt_slider_knob')))
    slider = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.geetest_slider_button')))
    # 使用click_and_hold()方法悬停在滑块上，perform()方法用于执行
    ActionChains(browser).click_and_hold(slider).perform()

    ActionChains(browser).move_by_offset(xoffset=100, yoffset=0).perform()
    ActionChains(browser).move_by_offset(xoffset=-100, yoffset=0).perform()

    for x in trace:
        # 使用move_by_offset()方法拖动滑块，perform()方法用于执行
        ActionChains(browser).move_by_offset(xoffset=x, yoffset=0).perform()
    # 模拟人类对准时间
    time.sleep(0.5)
    # 释放滑块
    ActionChains(browser).release().perform()


def slide():
    distance = get_distance(Image.open('.\\bili_back.png'), Image.open('.\\bili_full.png'))
    print('计算偏移量为：%s Px' % distance)
    # 计算移动轨迹
    trace = get_trace(distance - 5)
    # 移动滑块
    move_to_gap(trace)
    time.sleep(3)


init()
login()
cut()
slide()
