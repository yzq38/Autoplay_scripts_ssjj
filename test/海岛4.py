import pyautogui
import cv2
import numpy as np
import time
import random

import pynput
from PIL import Image
import os
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
import ctypes
from ctypes import wintypes, Structure, POINTER, c_ulong
import sys


class AutoBot:
    def __init__(self):
        # 禁用pyautogui的故障安全功能，避免冲突
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.5
        self.templates = {}
        self.level_states = {}  # 存储关卡的不同状态

        # 使用pynput的控制器
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()

        # 加载Windows API
        self.user32 = ctypes.windll.user32

    def test_pyautogui_functionality(self):
        """测试 pyautogui 基本功能"""
        print("测试 pyautogui 功能...")

        # 获取屏幕尺寸
        screen_width, screen_height = pyautogui.size()
        print(f"屏幕尺寸: {screen_width}x{screen_height}")

        # 测试鼠标移动
        test_x, test_y = 100, 100
        print(f"测试移动到: ({test_x}, {test_y})")

        try:
            pyautogui.moveTo(test_x, test_y, duration=1)

            # 检查是否移动成功
            current_x, current_y = pyautogui.position()
            print(f"移动后位置: ({current_x}, {current_y})")

            if abs(current_x - test_x) < 10 and abs(current_y - test_y) < 10:
                print("✓ 鼠标移动测试通过")

                # 测试点击
                print("测试点击操作")
                pyautogui.click()
                print("✓ 点击测试完成")
                return True
            else:
                print("✗ 鼠标移动测试失败")
                return False
        except Exception as e:
            print(f"pyautogui测试出错: {e}")
            print("尝试使用备用方法...")
            return self.test_alternative_functionality()

    def test_alternative_functionality(self):
        """备用功能测试方法"""
        print("使用备用方法测试功能...")

        try:
            # 使用pynput测试
            original_pos = self.mouse_controller.position
            test_x, test_y = 200, 200

            self.mouse_controller.position = (test_x, test_y)
            time.sleep(0.5)

            new_pos = self.mouse_controller.position
            print(f"移动后位置: {new_pos}")

            if abs(new_pos[0] - test_x) < 10 and abs(new_pos[1] - test_y) < 10:
                print("✓ 备用鼠标移动测试通过")
                return True
            else:
                print("✗ 备用鼠标移动测试失败")
                return False

        except Exception as e:
            print(f"备用测试也失败: {e}")
            return False

    def move_mouse_win32(self, x_offset, y_offset, duration=0.5):
        """使用Windows API模拟鼠标相对移动"""
        print(f"使用Windows API模拟鼠标相对移动: x={x_offset}, y={y_offset}, 持续时间={duration}秒")

        try:
            # 计算步数和每步的延迟
            steps = max(1, int(duration * 20))  # 每步0.05秒
            step_delay = duration / steps
            step_x = int(x_offset / steps)
            step_y = int(y_offset / steps)

            for i in range(steps):
                # 使用mouse_event API (兼容性更好)
                self.user32.mouse_event(0x0001, step_x, step_y, 0, 0)
                time.sleep(step_delay)

        except Exception as e:
            print(f"Windows API移动失败: {e}")
            # 备用方法：使用pynput
            print("使用pynput备用方法")
            self.move_mouse_pynput(x_offset, y_offset, duration)

    def move_mouse_pynput(self, x_offset, y_offset, duration=0.5):
        """使用pynput模拟鼠标相对移动"""
        print(f"使用pynput模拟鼠标相对移动: x={x_offset}, y={y_offset}, 持续时间={duration}秒")

        # 计算步长和每一步的延迟
        steps = int(duration * 100)  # 每步0.01秒，总共steps步
        if steps == 0:
            steps = 1
        step_x = x_offset / steps
        step_y = y_offset / steps
        step_delay = duration / steps

        for i in range(steps):
            self.mouse_controller.move(step_x, step_y)
            time.sleep(step_delay)

    def mouse_click_win32(self, button='left'):
        """使用Windows API模拟鼠标点击"""
        try:
            if button == 'left':
                self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # 左键按下
                time.sleep(0.2)
                self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # 左键释放
            elif button == 'right':
                self.user32.mouse_event(0x0008, 0, 0, 0, 0)  # 右键按下
                time.sleep(0.5)
                self.user32.mouse_event(0x0010, 0, 0, 0, 0)  # 右键释放
            elif button == 'middle':
                self.user32.mouse_event(0x0020, 0, 0, 0, 0)  # 中键按下
                time.sleep(0.2)
                self.user32.mouse_event(0x0040, 0, 0, 0, 0)  # 中键释放

        except Exception as e:
            print(f"Windows API点击失败: {e}")
            # 备用方法
            if button == 'left':
                self.mouse_controller.click(pynput.mouse.Button.left)
            elif button == 'right':
                self.mouse_controller.click(pynput.mouse.Button.right)
            elif button == 'middle':
                self.mouse_controller.click(pynput.mouse.Button.middle)

    def mouse_down_win32(self, button='left'):
        """使用Windows API模拟鼠标按下"""
        try:
            if button == 'left':
                self.user32.mouse_event(0x0002, 0, 0, 0, 0)
            elif button == 'right':
                self.user32.mouse_event(0x0008, 0, 0, 0, 0)
            elif button == 'middle':
                self.user32.mouse_event(0x0020, 0, 0, 0, 0)
        except Exception as e:
            print(f"Windows API按下失败: {e}")

    def mouse_up_win32(self, button='left'):
        """使用Windows API模拟鼠标释放"""
        try:
            if button == 'left':
                self.user32.mouse_event(0x0004, 0, 0, 0, 0)
            elif button == 'right':
                self.user32.mouse_event(0x0010, 0, 0, 0, 0)
            elif button == 'middle':
                self.user32.mouse_event(0x0040, 0, 0, 0, 0)
        except Exception as e:
            print(f"Windows API释放失败: {e}")

    def boss_ready_operations(self):
        """检测到boss战准备时执行的操作"""
        print("检测到boss战准备，执行特定操作...")

        self.keyboard_controller.press('3')
        time.sleep(0.2)
        self.keyboard_controller.release('3')
        time.sleep(0.5)
        self.keyboard_controller.press('e')
        time.sleep(0.2)
        self.keyboard_controller.release('e')
        time.sleep(0.5)
        self.keyboard_controller.press('1')
        time.sleep(0.2)
        self.keyboard_controller.release('1')
        time.sleep(0.5)
        self.keyboard_controller.press('4')
        time.sleep(0.1)
        self.keyboard_controller.release('4')
        time.sleep(0.5)
        self.keyboard_controller.press('1')
        time.sleep(0.1)
        self.keyboard_controller.release('1')

        print("boss战准备操作完成")

    def game_internal_operations(self):
        """游戏内操作（硬编码）匹配度"""
        print("开始执行游戏内操作...")
        kazhu = False
        # 等待游戏完全加载
        print("等待游戏完全加载...")
        for i in range(60):
            if self.find_game_element():
                time.sleep(4)
                break
            elif i == 58:
                kazhu = True
                break
            else:
                time.sleep(1)
        if not kazhu:
            try:
                # 初始操作
                screen_width, screen_height = pyautogui.size()
                center_x, center_y = screen_width // 2, screen_height // 2
                print(f"移动到屏幕中心: ({center_x}, {center_y})")

                self.mouse_controller.position = (center_x, center_y)
                self.mouse_click_win32('left')
                time.sleep(1)
                self.mouse_click_win32('left')
                self.keyboard_controller.press('a')
                time.sleep(2)
                self.keyboard_controller.release('a')
                time.sleep(0.5)
                self.mouse_click_win32('left')
                self.keyboard_controller.press('s')
                time.sleep(2)
                self.keyboard_controller.release('s')
                time.sleep(0.5)
                self.move_mouse_win32(500, 0, duration=0.5)
                time.sleep(0.5)
                self.mouse_click_win32('left')
                time.sleep(0.5)
                self.move_mouse_win32(100, 0, duration=0.5)
                time.sleep(0.5)
                self.mouse_click_win32('left')
                time.sleep(0.5)
                self.move_mouse_win32(200, 0, duration=0.5)
                time.sleep(0.5)
                self.mouse_click_win32('left')
                time.sleep(0.5)
                self.keyboard_controller.press('2')
                time.sleep(0.1)
                self.keyboard_controller.release('2')
                time.sleep(0.5)
                self.move_mouse_win32(0, 600, duration=0.5)
                time.sleep(0.5)
                self.mouse_click_win32('right')
                time.sleep(1)
                self.mouse_click_win32('left')
                time.sleep(3)
                self.move_mouse_win32(0, -600, duration=0.5)
                time.sleep(0.5)
                self.move_mouse_win32(-100, 0, duration=0.5)
                time.sleep(0.5)
                self.move_mouse_win32(-700, 0, duration=0.5)
                time.sleep(0.5)
                self.keyboard_controller.press('1')
                time.sleep(0.1)
                self.keyboard_controller.release('1')
                self.mouse_down_win32('left')
                time.sleep(3)
                self.mouse_up_win32('left')
                time.sleep(0.5)
                self.move_mouse_win32(-1400, 0, duration=0.5)
                time.sleep(0.5)

                for i in range(400):
                    if self.find_success(0.8):
                        time.sleep(1)
                        print("等待结算")
                        break
                    time.sleep(1)
                    if (i + 10) % 32 == 10:
                        self.keyboard_controller.press('4')
                        time.sleep(0.1)
                        self.keyboard_controller.release('4')
                        time.sleep(0.5)
                        if self.find_success(0.8):
                            time.sleep(1)
                            print("等待结算")
                            break
                        self.keyboard_controller.press('3')
                        time.sleep(0.1)
                        self.keyboard_controller.release('3')
                        time.sleep(0.5)
                        if self.find_success(0.8):
                            time.sleep(1)
                            print("等待结算")
                            break
                        self.keyboard_controller.press('e')
                        time.sleep(0.1)
                        self.keyboard_controller.release('e')
                        time.sleep(0.5)
                        if self.find_success(0.8):
                            time.sleep(1)
                            print("等待结算")
                            break
                        self.keyboard_controller.press('1')
                        time.sleep(0.1)
                        self.keyboard_controller.release('1')
                        time.sleep(0.5)
                        if self.find_success(0.8):
                            time.sleep(1)
                            print("等待结算")
                            break
                        self.mouse_click_win32('middle')
                self.mouse_down_win32('left')
                time.sleep(5)
                self.mouse_up_win32('left')

                if self.find_success(0.8):
                    time.sleep(1)
                    print("等待结算")

                # 短暂休眠，避免过于频繁的检测

                time.sleep(0.5)

                print("游戏内操作完成")
                return False

            except Exception as e:
                print(f"游戏内操作出错: {e}")
                return False
        else :
            self.mouse_click_win32('left')
            time.sleep(1)
            self.mouse_click_win32('left')
            if self.wait_for_template("close_window",timeout=50):
                self.click_template("close_window")
                time.sleep(30)
                if self.find_on_screen("返回游戏大厅"):
                    self.click_template("返回游戏大厅")
                    return 1
                else:
                    time.sleep(3)
                    self.mouse_click_win32('left')
                    time.sleep(1)
                    self.click_template("退出队伍")
                    return 1

    def find_success(self, confidence=0.8):
        is_success = self.find_on_screen("mission_success", confidence)
        if is_success:
            print("任务完成，进入等待结算状态")
            return is_success

        return None

    def find_loading(self, confidence=0.88):
        "检测加载页面"
        screen_loading = self.find_on_screen("loading", confidence)
        if screen_loading:
            print("加载成功，开始等待进入游戏")
            return screen_loading
        return None

    def find_boss_ready(self, confidence=0.8):
        boss = self.find_on_screen("boss_ready", confidence)
        if boss:
            print("boss战")
            return boss
        return None

    def find_game_element(self, confidence=0.93):
        game_element = self.find_on_screen("game_element", confidence)
        if game_element:
            print("找到页面元素，正式游戏")
            return game_element
        return None

    def load_template(self, name, image_path):
        """加载图像模板用于屏幕匹配 - 使用PIL读取"""
        try:
            if not os.path.exists(image_path):
                print(f"模板文件不存在: {image_path}")
                return False

            # 使用PIL读取图片并转换为灰度图
            pil_image = Image.open(image_path)
            if pil_image.mode != 'L':
                pil_image = pil_image.convert('L')

            template = np.array(pil_image)

            if template is None:
                print(f"无法加载模板: {name}")
                return False

            h, w = template.shape
            print(f"成功加载模板: {name}, 尺寸: {w}x{h}")

            self.templates[name] = template
            return True

        except Exception as e:
            print(f"加载模板 {name} 失败: {e}")
            return False

    def load_level_states(self, level_name, state_files):
        """加载关卡的不同状态模板"""
        self.level_states[level_name] = {}
        success_count = 0

        for state_name, file_path in state_files.items():
            if self.load_template(f"{level_name}_{state_name}", file_path):
                self.level_states[level_name][state_name] = f"{level_name}_{state_name}"
                success_count += 1

        print(f"为关卡 {level_name} 加载了 {success_count}/{len(state_files)} 个状态")
        return success_count > 0

    def load_all_templates(self):
        """加载所有模板"""
        templates_to_load = {
            "level_selection": "海岛4.png",
            "nightmare_difficulty": "噩梦.png",
            "expert_difficulty": "专家.png",
            "initial_difficulty": "初始难度.png",
            "special_reward_difficulty": "特殊奖励难度.png",
            "room_encryption": "房间加密.png",
            "friend_only": "仅好友.png",
            "enter_battle": "进入战斗.png",
            "start_battle": "开始战斗.png",
            "settlement_confirm": "确定.png",
            "settlement_confirm2": "确定2.png",
            "exit_button": "退出.png",
            "返回游戏大厅": "返回游戏大厅.png",
            "退出队伍": "退出队伍.png",
            "challenge_count_zero": "挑战次数0.png",
            "boss_ready": "boss战准备.png",
            "mission_success": "任务成功.png",
            "loading": "加载中.png",
            "blacklist": "黑名单.png",
            "game_element": "游戏元素.png",
            "nextpage": "下一页.png",
            "change_gun": "背包23.png",
            "fuwen": "符文仓库.png",
            "mainhall": "营地大厅.png",
            "changefuwen_to3": "符文背包3.png",
            "x": "叉号.png",
            "backtogame": "返回关卡.png",
            "close_window": "关闭程序.png",
        }

        success_count = 0
        for name, path in templates_to_load.items():
            if self.load_template(name, path):
                success_count += 1

        # 加载关卡状态
        haidao4_states = {
            "state1": "海岛4.png",
            "state2": "海岛4_2.png",
            "state3": "海岛4_3.png",
        }
        self.load_level_states("haidao4", haidao4_states)

        print(f"成功加载 {success_count}/{len(templates_to_load)} 个模板")
        return success_count > 0

    def find_on_screen(self, template_name, confidence=0.6, region=None):
        """在屏幕上查找指定的模板图像"""
        if template_name not in self.templates:
            print(f"未找到模板: {template_name}")
            return None

        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            template = self.templates[template_name]

            t_h, t_w = template.shape
            s_h, s_w = screenshot_gray.shape

            if t_h > s_h or t_w > s_w:
                print(f"模板 {template_name} 尺寸 {t_w}x{t_h} 大于屏幕截图 {s_w}x{s_h}，无法匹配")
                return None

            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            print(f"模板 {template_name} 匹配度: {max_val:.3f}")

            if max_val >= confidence:
                h, w = template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2

                # 如果指定了区域，需要调整坐标
                if region:
                    center_x += region[0]
                    center_y += region[1]

                print(f"找到模板 {template_name} 在位置 ({center_x}, {center_y})")
                return (center_x, center_y)
            else:
                print(f"模板 {template_name} 匹配度 {max_val:.3f} 低于阈值 {confidence}")
                return None

        except Exception as e:
            print(f"在查找模板 {template_name} 时发生错误: {e}")
            return None

    def find_level_with_states(self, level_name, confidence=0.7):
        """查找关卡，检查所有可能的状态"""
        if level_name not in self.level_states:
            print(f"未找到关卡状态配置: {level_name}")
            return None

        states = self.level_states[level_name]
        best_match = None
        best_confidence = 0

        for state_name, template_name in states.items():
            pos = self.find_on_screen(template_name, confidence)
            if pos:
                current_confidence = self.get_template_confidence(template_name)
                if current_confidence > best_confidence:
                    best_confidence = current_confidence
                    best_match = pos
                    print(f"找到关卡 {level_name} 状态 {state_name}, 置信度: {best_confidence:.3f}")

        return best_match

    def get_template_confidence(self, template_name, region=None):
        """获取模板匹配的置信度"""
        if template_name not in self.templates:
            return 0

        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            template = self.templates[template_name]

            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            return max_val
        except Exception as e:
            print(f"获取模板置信度失败: {e}")
            return 0

    def click_at_position(self, pos, delay=0.5):
        """在指定位置点击"""
        if pos:
            print(f"准备移动到位置: ({pos[0]}, {pos[1]})")

            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            print(f"当前鼠标位置: ({current_x}, {current_y})")

            # 移动鼠标
            move_duration = random.uniform(0.2, 0.5)
            print(f"移动持续时间: {move_duration:.2f}秒")
            pyautogui.moveTo(pos[0], pos[1], duration=move_duration)

            # 验证移动是否成功
            new_x, new_y = pyautogui.position()
            print(f"移动后鼠标位置: ({new_x}, {new_y})")

            if abs(new_x - pos[0]) > 10 or abs(new_y - pos[1]) > 10:
                print("警告: 鼠标移动未到达目标位置")

            time.sleep(delay)

            # 执行点击
            print("执行点击操作")
            pyautogui.click()

            # 验证点击后位置
            after_click_x, after_click_y = pyautogui.position()
            print(f"点击后鼠标位置: ({after_click_x}, {after_click_y})")

            return True
        return False

    def click_template(self, template_name, confidence=0.85, delay=0.5, max_retry=7):
        """查找并点击模板图像 - 增强版本"""
        for i in range(max_retry):
            pos = self.find_on_screen(template_name, confidence)
            if pos:
                if self.click_at_position(pos, delay):
                    print(f"成功点击: {template_name}")
                    return True
            else:
                # 如果找不到模板，尝试备用方法
                if template_name == "expert_difficulty":
                    print("专家难度未找到，尝试备用点击位置")
                    # 根据噩梦难度的位置推算专家难度的位置
                    nightmare_pos = self.find_on_screen("nightmare_difficulty", confidence=0.8)
                    if nightmare_pos:
                        # 假设专家难度在噩梦难度下方固定距离
                        expert_x = nightmare_pos[0]
                        expert_y = nightmare_pos[1] + 80  # 调整这个值
                        if self.click_at_position((expert_x, expert_y), delay):
                            print(f"通过备用位置点击专家难度")
                            return True

            print(f"第{i + 1}次尝试点击 {template_name} 失败")
            time.sleep(1)

        print(f"无法找到或点击: {template_name}")
        return False

    def click_level_with_states(self, level_name, confidence=0.899, delay=0.5, max_retry=7):
        """点击关卡，考虑所有可能的状态"""
        for i in range(max_retry):
            pos = self.find_level_with_states(level_name, confidence)
            if pos:
                if self.click_at_position(pos, delay):
                    print(f"成功点击关卡: {level_name}")
                    return True

            print(f"第{i + 1}次尝试点击关卡 {level_name} 失败")
            time.sleep(1)

        print(f"无法找到或点击关卡: {level_name}")
        return False

    def random_click_in_region(self, x1, y1, x2, y2):
        """在指定区域内随机点击"""
        x = random.randint(x1, x2)
        y = random.randint(y1, y2)

        pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.5))
        time.sleep(0.2)
        pyautogui.click()

    def press_key(self, key, times=1, delay=0.1):
        """按指定按键"""
        for _ in range(times):
            pyautogui.press(key)
            time.sleep(delay)

    def wait_for_template(self, template_name, timeout=30, check_interval=1, exclusive_mode=False):
        """等待指定模板出现在屏幕上"""
        start_time = time.time()
        last_check_time = start_time

        print(f"开始等待模板: {template_name}, 超时时间: {timeout}秒")

        while time.time() - start_time < timeout:
            current_time = time.time()

            # 只在exclusive_mode下打印进度，避免过于频繁
            if exclusive_mode or current_time - last_check_time >= 5:
                elapsed = current_time - start_time
                print(f"等待 {template_name} ... 已等待 {elapsed:.1f}秒")
                last_check_time = current_time

            pos = self.find_on_screen(template_name)
            if pos:
                print(f"成功找到模板: {template_name}")
                return True

            time.sleep(check_interval)

        print(f"等待 {template_name} 超时 ({timeout}秒)")
        return False

    def find_settlement_confirm(self, confidence=0.88):
        """查找结算确认按钮，支持两种状态"""
        # 先尝试第一种状态
        pos1 = self.find_on_screen("settlement_confirm", confidence)
        if pos1:
            print("找到结算确认按钮（状态1）")
            return pos1
        pos2 = self.find_on_screen("settlement_confirm2", confidence)
        if pos2:
            print("找到结算确认按钮（状态1）")
            return pos2

        return None

    def click_settlement_confirm(self, confidence=0.8, delay=0.5, max_retry=3):
        """点击结算确认按钮"""
        for i in range(max_retry):
            pos = self.find_settlement_confirm(confidence)
            if pos:
                if self.click_at_position(pos, delay):
                    time.sleep(2)
                    self.mouse_click_win32('left')
                    print("成功点击结算确认按钮")
                    return True

            print(f"第{i + 1}次尝试点击结算确认按钮失败")
            time.sleep(1)

        print("无法找到或点击结算确认按钮")
        return False

    def wait_for_settlement(self, timeout=120):
        """专门等待游戏结算的确定按钮出现"""
        print("进入结算等待模式，专注检测确定按钮...")
        start_time = time.time()
        last_check_time = start_time

        while time.time() - start_time < timeout:
            current_time = time.time()

            # 每5秒打印一次进度
            if current_time - last_check_time >= 5:
                elapsed = current_time - start_time
                print(f"等待结算确定按钮 ... 已等待 {elapsed:.1f}秒")
                last_check_time = current_time

            # 检查结算确认按钮
            pos = self.find_settlement_confirm()
            if pos:
                print("成功找到结算确认按钮")
                return True

            time.sleep(2)  # 检查间隔

        print(f"等待结算确认按钮超时 ({timeout}秒)")
        return False

    def hold_mouse(self, duration=5):
        """长按鼠标左键"""
        print(f"长按鼠标左键 {duration} 秒")
        pyautogui.mouseDown()
        time.sleep(duration)
        pyautogui.mouseUp()

    def save_screenshot(self, filename):
        """保存当前屏幕截图"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            print(f"截图已保存: {filename}")
        except Exception as e:
            print(f"保存截图失败: {e}")

    def check_challenge_count_zero(self):
        """检查挑战次数是否为0"""
        print("检查挑战次数...")
        zero_pos = self.find_on_screen("challenge_count_zero", confidence=0.95)
        if zero_pos:
            print("✓ 检测到挑战次数为0，终止程序")
            return True
        else:
            print("✓ 挑战次数充足，继续执行")
            return False

    def main_loop(self):
        """主循环函数 - 实现完整的游戏操作流程"""
        print("自动挂机脚本启动，5秒后开始...")
        time.sleep(5)

        cycle_count = 0

        while True:
            cycle_count += 1
            print(f"开始第 {cycle_count} 轮循环")

            try:
                # 1. 点击关卡编号（使用状态识别）
                if not self.click_level_with_states("haidao4", max_retry=5):
                    print("无法找到关卡选择，跳过本轮")
                    continue
                time.sleep(1)

                # 2. 点击噩梦难度
                if not self.click_template("nightmare_difficulty"):
                    print("无法找到噩梦难度，尝试其他难度...")
                    continue
                time.sleep(1)

                # 3. 点击专家难度
                if not self.click_template("expert_difficulty"):
                    print("无法找到专家难度")
                    continue
                time.sleep(1)

                # 4. 点击1.初始难度
                if not self.click_template("initial_difficulty"):
                    print("无法找到初始难度")
                    continue
                time.sleep(1)

                # 5. 点击5.特殊奖励难度
                if not self.click_template("special_reward_difficulty"):
                    print("无法找到特殊奖励难度")
                    continue
                time.sleep(1)

                # 检查挑战次数
                print("点击特殊奖励难度后，检查挑战次数...")
                if self.check_challenge_count_zero():
                    print("挑战次数已用尽，程序退出")
                    self.click_template("change_gun")
                    time.sleep(10)
                    self.click_template("mainhall")
                    time.sleep(10)
                    self.click_template("fuwen")
                    time.sleep(10)
                    self.move_mouse_win32(0, 100, duration=0.5)
                    self.click_template("changefuwen_to3")
                    time.sleep(10)
                    self.click_template("x")
                    time.sleep(10)
                    self.click_template("backtogame")
                    time.sleep(10)
                    self.click_template("nextpage")
                    break  # 跳出循环，终止程序

                # 6. 点击房间加密按钮
                if not self.click_template("room_encryption"):
                    print("无法找到房间加密按钮")
                    continue
                time.sleep(1)

                # 7. 点击黑名单左侧方块
                if not self.click_template("blacklist"):
                    print("无法找到选项")
                    continue
                time.sleep(1)

                # 8. 点击进入战斗
                if not self.click_template("enter_battle"):
                    print("无法找到进入战斗按钮")
                    continue
                time.sleep(1)

                # 9. 点击开始战斗
                if not self.click_template("start_battle"):
                    print("无法找到开始战斗按钮")
                    continue

                # 10. 等待进入关卡，同时持续检测返回游戏大厅按钮
                print("等待进入关卡，同时持续检测返回游戏大厅按钮...")
                lobby_continuously_detected = True

                # 持续30秒，每秒检测一次返回游戏大厅按钮
                for i in range(60):
                    time.sleep(1)
                    if self.find_loading(0.88):
                        print("进入游戏，停止返回检测")
                        lobby_continuously_detected = False
                        break
                    # 检测返回游戏大厅按钮
                    if not self.find_on_screen("返回游戏大厅", confidence=0.7):
                        print(f"第{i + 1}秒未检测到返回游戏大厅按钮")
                        lobby_continuously_detected = False

                    else:
                        if i >= 50:
                            print(f"第{i + 1}秒检测到返回游戏大厅按钮")
                            lobby_continuously_detected = True
                            break

                # 如果连续30秒都检测到返回游戏大厅按钮，执行恢复流程
                if lobby_continuously_detected:
                    print("连续30秒检测到返回游戏大厅按钮，确认未成功进入游戏，执行恢复流程...")

                    # 点击返回游戏大厅按钮
                    if self.click_template("返回游戏大厅", confidence=0.7, max_retry=3):
                        print("已点击返回游戏大厅按钮")
                        time.sleep(20)

                        # 等待并点击退出队伍按钮
                        if self.wait_for_template("退出队伍", timeout=10, check_interval=1):
                            if self.click_template("退出队伍", confidence=0.7, max_retry=3):
                                time.sleep(1)
                                self.click_template("退出队伍", confidence=0.7, max_retry=3)
                                print("已点击退出队伍按钮，准备重新开始循环")
                                time.sleep(3)
                                continue  # 重新开始主循环
                            else:
                                print("无法点击退出队伍按钮")
                        else:
                            print("未找到退出队伍按钮")
                    else:
                        print("无法点击返回游戏大厅按钮")

                    # 如果恢复流程失败，也重新开始循环
                    print("恢复流程完成或失败，重新开始循环")
                    continue

                # 11. 执行持续监控的游戏内操作
                print("确认成功进入游戏，开始执行持续监控的游戏内操作...")
                kazhule = self.game_internal_operations()
                if kazhule:
                    continue

                # 等待结算页面
                if not self.wait_for_settlement(timeout=240):
                    print("未检测到结算页面，尝试继续...")

                # 点击确定
                if not self.click_settlement_confirm(max_retry=3):
                    print("无法找到确定按钮")

                time.sleep(2)

                # 点击退出
                if not self.click_template("exit_button", max_retry=3):
                    print("无法找到退出按钮")

                time.sleep(3)

                # 随机休息，避免检测
                rest_time = random.uniform(8, 10)
                print(f"休息 {rest_time:.1f} 秒")
                time.sleep(rest_time)

            except KeyboardInterrupt:
                print("用户中断脚本")
                break
            except Exception as e:
                print(f"发生错误: {e}")
                # 保存错误截图
                self.save_screenshot(f"error_cycle_{cycle_count}.png")
                time.sleep(5)


# 使用示例
if __name__ == "__main__":
    bot = AutoBot()

    if bot.load_all_templates():
        print("所有模板加载成功，开始执行脚本...")
        bot.main_loop()
        print("程序正常结束")
        sys.exit(0)
    else:
        print("模板加载失败，请检查图片文件")
        sys.exit(1)