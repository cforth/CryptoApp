import io
import os
import logging
import tkinter.filedialog as filedialog
from libs.GifHandle import *
from libs.json2gui import *
from libs.CFCrypto import ByteCrypto, StringCrypto

logging.basicConfig(level=logging.INFO)


# 窗口类
class Window(ttk.Frame):
    def __init__(self, ui_json, master=None):
        super().__init__(master)
        # 从json自动设置UI控件
        create_ui(self, ui_json)
        # 从json自动绑定事件
        create_all_binds(self, ui_json)
        # 支持的图片格式后缀
        self.img_ext = [".bmp", ".gif", ".jpg", ".png", ".tiff", ".ico", ".jpeg"]
        # 存储GIF动图对象，若不存储，图片对象会被垃圾回收无法显示
        self.gif = None
        # 存储静态图片对象，若不存储，图片对象会被垃圾回收无法显示
        self.img = None
        # 存储图片地址列表，用于前后翻页
        self.img_list = []
        # 保存当前的图片路径
        self.current_img_path = ""
        # 初始化下拉列表，设置默认值
        self.init_default_combobox_item()
        # 设置图片最大的宽度(gif图片不能缩放)
        self.img_max_width = 1280
        # 设置默认的图片宽度，并设置图片大小滑动条的位置
        self.img_width = self.img_max_width * 0.45
        # 图片需要逆时针旋转的角度
        self.rotate_angle = 0
        self.__dict__["imgSizeScale"].set(self.img_width * 100 / self.img_max_width)
        self.__dict__["imgSizeInfo"].set(str(self.img_width * 100 // self.img_max_width) + "%")
        # 绑定键盘事件
        self.master.bind("<Key>", self.key_event)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

    # 初始化下拉列表，设置默认值
    def init_default_combobox_item(self):
        # 设置默认的选项
        set_combobox_item(self.__dict__["cryptoOptionCombobox"], "不需解密", True)
        # 设置单页显示
        set_combobox_item(self.__dict__["pageOptionCombobox"], "单页", True)
        # 设置双页阅读顺序
        set_combobox_item(self.__dict__["orderOptionCombobox"], "左开", True)

    # 根据图片路径，将当前文件夹内所有图片保存在图片列表，用于前后翻页显示
    def set_img_list(self):
        img_dir_path = self.current_img_path[:self.current_img_path.rindex("/") + 1]
        crypto_option = self.__dict__["cryptoOption"].get()
        if crypto_option == "解密文件":
            self.img_list = []
            for img_name in os.listdir(img_dir_path):
                try:
                    decrypt_img_name = StringCrypto(self.__dict__["password"].get()).decrypt(img_name)
                    if os.path.splitext(decrypt_img_name.lower())[1] in self.img_ext:
                        self.img_list.append(os.path.join(img_dir_path, img_name))
                except Exception as e:
                    logging.error("Decrypt img name error!")

        elif crypto_option == "解密保名" or crypto_option == "不需解密":
            self.img_list = [os.path.join(img_dir_path, img_name) for img_name in os.listdir(img_dir_path)
                             if os.path.splitext(img_name.lower())[1] in self.img_ext]

    # 设置显示图片信息
    def set_img_info(self):
        page_option = self.__dict__["pageOption"].get()
        if not self.img_list or self.current_img_path not in self.img_list:
            self.__dict__["imgInfoL"].set("")
            self.__dict__["imgInfoR"].set("")
        elif page_option == "单页":
            img_index = self.img_list.index(self.current_img_path)
            index_str = str(img_index + 1) + "/" + str(len(self.img_list))
            img_name = os.path.basename(self.current_img_path)
            self.__dict__["imgInfoL"].set(index_str + " | " + img_name)
            self.__dict__["imgInfoR"].set("")
        elif page_option == "双页":
            img_index = self.img_list.index(self.current_img_path)
            index_str = str(img_index + 1) + "/" + str(len(self.img_list))
            img_name = os.path.basename(self.current_img_path)
            if img_index < len(self.img_list) - 1:
                img_index_next = img_index + 1
                index_str_next = str(img_index_next + 1) + "/" + str(len(self.img_list))
                img_name_next = os.path.basename(self.img_list[img_index_next])
                order_option = self.__dict__["orderOption"].get()
                if order_option == "左开":
                    self.__dict__["imgInfoL"].set(index_str + " | " + img_name)
                    self.__dict__["imgInfoR"].set(index_str_next + " | " + img_name_next)
                else:
                    self.__dict__["imgInfoR"].set(index_str + " | " + img_name)
                    self.__dict__["imgInfoL"].set(index_str_next + " | " + img_name_next)
            else:
                self.__dict__["imgInfoL"].set(index_str + " | " + img_name)

    def key_event(self, event=None):
        # 右方向键下一张图片
        if event.keycode == 39:
            self.next_img_button_callback()
        # 左方向键上一张图片
        elif event.keycode == 37:
            self.prev_img_button_callback()

    # 选择待显示的图片，填充图片路径，设置图片地址列表
    def file_from_button_callback(self, event=None):
        img_path = filedialog.askopenfilename()
        if img_path:
            self.current_img_path = img_path
            self.set_img_list()
            self.set_img_info()
            self.img_show()

    # 重新加载图片
    def refresh_button_callback(self, event=None):
        self.set_img_info()
        self.img_show()

    # 设置密码输入栏中的内容显示或者隐藏
    def password_show_button_callback(self, event=None):
        if self.__dict__["passwordEntry"]["show"] == "*":
            self.__dict__["passwordEntry"]["show"] = ""
        else:
            self.__dict__["passwordEntry"]["show"] = "*"

    # 向前翻页显示图片
    def prev_img_button_callback(self, event=None):
        page_option = self.__dict__["pageOption"].get()
        self.rotate_angle = 0
        if not self.img_list:
            return
        elif self.current_img_path not in self.img_list:
            index = len(self.img_list)
        else:
            index = self.img_list.index(self.current_img_path)

        if page_option == "单页":
            if index == 0:
                return
            else:
                self.current_img_path = self.img_list[index - 1]
        elif page_option == "双页":
            if index == 0:
                return
            elif index == 1:
                self.current_img_path = self.img_list[index - 1]
            else:
                self.current_img_path = self.img_list[index - 2]

        self.set_img_info()
        self.img_show()

    # 向后翻页显示图片
    def next_img_button_callback(self, event=None):
        page_option = self.__dict__["pageOption"].get()
        self.rotate_angle = 0
        if not self.img_list:
            return
        elif self.current_img_path not in self.img_list:
            index = -1
        else:
            index = self.img_list.index(self.current_img_path)

        if page_option == "单页":
            if index == len(self.img_list) - 1:
                return
            else:
                self.current_img_path = self.img_list[index + 1]
        elif page_option == "双页":
            if index == len(self.img_list) - 1:
                return
            elif index == len(self.img_list) - 2:
                self.current_img_path = self.img_list[index + 1]
            else:
                self.current_img_path = self.img_list[index + 2]

        self.set_img_info()
        self.img_show()

    # 逆时针旋转图片
    def rotate_img_button_callback(self, event=None):
        # 逆时针旋转90度
        self.rotate_angle += 90
        # 超过360度取余
        self.rotate_angle %= 360
        self.img_show()

    # 拖动图片大小滑动条时，显示图片大小百分比
    def set_img_size_info(self, event=None):
        self.img_width = int(self.__dict__["imgSizeScale"].get() * self.img_max_width / 100)
        self.__dict__["imgSizeInfo"].set(str(self.img_width * 100 // self.img_max_width) + "%")

    # 设置当前显示的图片的大小，保持横纵比缩放
    def set_img_width(self, event=None):
        self.set_img_size_info()
        self.img_show()

    # 读取图片
    def default_img_read(self, img_path):
        # 根据rotate_angle逆时针旋转图片
        if self.rotate_angle == 0 or self.rotate_angle == 180:
            img_data = Image.open(img_path).rotate(self.rotate_angle, expand=True)  # 旋转图像, 长宽调整
            x, y = img_data.size
            x_s = int(self.img_width)
            # 调整图片大小时保持横纵比
            y_s = int(y * x_s // x)
        elif self.rotate_angle == 90 or self.rotate_angle == 270:
            img_data = Image.open(img_path).rotate(self.rotate_angle, expand=True)  # 旋转图像, 长宽调整
            x, y = img_data.size
            y_s = int(self.img_width)
            # 调整图片大小时保持横纵比
            x_s = int(x * y_s // y)
        else:
            img_data = Image.open(img_path).rotate(self.rotate_angle)  # 旋转图像, 长宽不变
            x, y = img_data.size
            x_s = int(self.img_width)
            # 调整图片大小时保持横纵比
            y_s = int(y * x_s // x)

        return img_data.resize((x_s, y_s), Image.ANTIALIAS)

    # 静态图片显示
    def default_img_show(self, img_path):
        out = self.default_img_read(img_path)
        self.img = ImageTk.PhotoImage(out)
        self.__dict__["imgLabel"].configure(image=self.img)

    # 双页静态图片显示
    def default_double_img_show(self, img_path, next_img_path):
        # 双页显示的顺序设定
        order_option = self.__dict__["orderOption"].get()
        current_out = self.default_img_read(img_path)
        next_out = self.default_img_read(next_img_path)
        current_x, current_y = current_out.size
        current_x_s = int(self.img_width)
        current_y_s = int(current_y * current_x_s // current_x)
        next_x, next_y = next_out.size
        next_x_s = int(self.img_width)
        next_y_s = int(next_y * next_x_s // next_x)
        # 将两张图片合并为一张图片
        to_image = Image.new('RGBA', (current_x_s + next_x_s, current_y_s if current_y_s > next_y_s else next_y_s))
        if order_option == "左开":
            to_image.paste(current_out, (0, 0))
            to_image.paste(next_out, (current_x_s, 0))
        elif order_option == "右开":
            to_image.paste(next_out, (0, 0))
            to_image.paste(current_out, (next_x_s, 0))
        self.img = ImageTk.PhotoImage(to_image)
        self.__dict__["imgLabel"].configure(image=self.img)

    # 加密静态图片显示
    def crypto_img_show(self, img_path):
        img_file_like = io.BytesIO(ByteCrypto(self.__dict__["password"].get()).decrypt(img_path))
        self.default_img_show(img_file_like)

    # 双页加密静态图片显示
    def crypto_double_img_show(self, img_path, next_img_path):
        img_file_like = io.BytesIO(ByteCrypto(self.__dict__["password"].get()).decrypt(img_path))
        next_img_file_like = io.BytesIO(ByteCrypto(self.__dict__["password"].get()).decrypt(next_img_path))
        self.default_double_img_show(img_file_like, next_img_file_like)

    # 动态图片显示
    def default_gif_show(self, img_path):
        # 建立gif动图处理类
        self.gif = GifHandle(self.__dict__["imgLabel"], img_path, self.rotate_angle)
        self.gif.start_gif()

    # 加密动态图片显示
    def crypto_gif_show(self, img_path):
        img_file_like = io.BytesIO(ByteCrypto(self.__dict__["password"].get()).decrypt(img_path))
        self.default_gif_show(img_file_like)

    # 清空图片显示
    def cancel_img(self):
        # 如果有GIF动图正在运行，则停止这个定时事件
        if self.gif:
            self.gif.stop_gif()
        self.img = None
        self.gif = None
        self.__dict__["imgLabel"].config(image='')

    # 根据不同图片类型和解密选项，显示图片
    def img_show(self, event=None):
        page_option = self.__dict__["pageOption"].get()
        self.cancel_img()
        crypto_option = self.__dict__["cryptoOption"].get()
        # 如果路径不存在直接返回
        if not self.current_img_path or not os.path.exists(self.current_img_path):
            return
        img_name = os.path.basename(self.current_img_path)
        if crypto_option == "解密文件":
            decrypt_img_name = StringCrypto(self.__dict__["password"].get()).decrypt(img_name)
            # 如果图片后缀不支持，则直接返回
            if os.path.splitext(decrypt_img_name.lower())[1] not in self.img_ext:
                self.__dict__["imgInfoL"].set("文件格式不支持")
                return
            if os.path.splitext(decrypt_img_name)[1] == ".gif":
                self.crypto_gif_show(self.current_img_path)
            elif page_option == "单页":
                self.crypto_img_show(self.current_img_path)
            elif page_option == "双页":
                index = self.img_list.index(self.current_img_path)
                # 如果已经到了最后一页，则只显示一页
                if index == len(self.img_list) - 1:
                    self.default_img_show(self.current_img_path)
                else:
                    next_img_path = self.img_list[index + 1]
                    self.crypto_double_img_show(self.current_img_path, next_img_path)
        elif crypto_option == "不需解密":
            # 如果图片后缀不支持，则直接返回
            if os.path.splitext(img_name.lower())[1] not in self.img_ext:
                self.__dict__["imgInfoL"].set("文件格式不支持")
                self.__dict__["imgInfoR"].set("")
                return
            if os.path.splitext(self.current_img_path)[1] == ".gif":
                self.default_gif_show(self.current_img_path)
            elif page_option == "单页":
                self.default_img_show(self.current_img_path)
            elif page_option == "双页":
                index = self.img_list.index(self.current_img_path)
                # 如果已经到了最后一页，则只显示一页
                if index == len(self.img_list) - 1:
                    self.default_img_show(self.current_img_path)
                else:
                    next_img_path = self.img_list[index + 1]
                    self.default_double_img_show(self.current_img_path, next_img_path)
        elif crypto_option == "解密保名":
            # 如果图片后缀不支持，则直接返回
            if os.path.splitext(img_name.lower())[1] not in self.img_ext:
                self.__dict__["imgInfoL"].set("文件格式不支持")
                self.__dict__["imgInfoR"].set("")
                return
            if os.path.splitext(self.current_img_path)[1] == ".gif":
                self.crypto_gif_show(self.current_img_path)
            elif page_option == "单页":
                self.crypto_img_show(self.current_img_path)
            elif page_option == "双页":
                index = self.img_list.index(self.current_img_path)
                # 如果已经到了最后一页，则只显示一页
                if index == len(self.img_list) - 1:
                    self.default_img_show(self.current_img_path)
                else:
                    next_img_path = self.img_list[index + 1]
                    self.crypto_double_img_show(self.current_img_path, next_img_path)


if __name__ == '__main__':
    app = Window("ImgLookUI.json")
    # 设置窗口标题:
    app.master.title("图片查看器")
    app.master.minsize(600, 600)
    # 主消息循环:
    app.mainloop()
