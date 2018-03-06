import io
import os
import tkinter.filedialog as filedialog
from libs.GifHandle import *
from libs.json2gui import *
from libs.CFCrypto import ByteCrypto, StringCrypto


# 窗口类
class Window(ttk.Frame):
    def __init__(self, ui_json, master=None):
        super().__init__(master)
        # 从json自动设置UI控件
        create_ui(self, ui_json)
        # 从json自动绑定事件
        create_all_binds(self, ui_json)
        # 支持的图片格式后缀
        self.img_ext = [".bmp", ".gif", ".jpg", ".png", ".tiff", ".ico"]
        # 存储GIF动图对象，若不存储，图片对象会被垃圾回收无法显示
        self.gif = None
        # 存储静态图片对象，若不存储，图片对象会被垃圾回收无法显示
        self.img = None
        # 存储图片地址列表，用于前后翻页
        self.img_list = []
        # 初始化下拉列表，设置默认值
        self.init_default_crypto_option()
        # 设置图片最大的宽度(gif图片不能缩放)
        self.img_max_width = 1280
        # 设置默认的图片宽度，并设置图片大小滑动条的位置
        self.img_width = self.img_max_width * 0.6
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
        self.rowconfigure(4, weight=1)

    # 初始化下拉列表，设置默认值
    def init_default_crypto_option(self):
        set_combobox_item(self.__dict__["cryptoOptionCombobox"], "不需解密", True)

    # 根据图片路径，将当前文件夹内所有图片保存在图片列表，用于前后翻页显示
    def set_img_list(self):
        img_path = getattr(self, "imgPath").get()
        img_dir_path = img_path[:img_path.rindex("/") + 1]
        self.img_list = [os.path.join(img_dir_path, img_name) for img_name in os.listdir(img_dir_path)
                         if os.path.splitext(img_name.lower())[1] in self.img_ext]

    def key_event(self, event=None):
        # 右方向键下一首
        if event.keycode == 39:
            self.next_img_button_callback()
        # 左方向键上一首
        elif event.keycode == 37:
            self.prev_img_button_callback()

    # 选择待显示的图片，填充图片路径，设置图片地址列表
    def file_from_button_callback(self, event=None):
        img_path = filedialog.askopenfilename()
        if img_path:
            self.__dict__["imgPath"].set(img_path)
            self.set_img_list()

    # 设置密码输入栏中的内容显示或者隐藏
    def password_show_button_callback(self, event=None):
        if self.__dict__["passwordEntry"]["show"] == "*":
            self.__dict__["passwordEntry"]["show"] = ""
        else:
            self.__dict__["passwordEntry"]["show"] = "*"

    # 向前翻页显示图片
    def prev_img_button_callback(self, event=None):
        self.rotate_angle = 0
        old_img_path = getattr(self, "imgPath").get()
        if not self.img_list:
            return
        elif old_img_path not in self.img_list:
            index = len(self.img_list)
        else:
            index = self.img_list.index(old_img_path)

        if index == 0:
            return
        else:
            new_music_path = self.img_list[index - 1]
            getattr(self, "imgPath").set(new_music_path)
            self.img_show()

    # 向后翻页显示图片
    def next_img_button_callback(self, event=None):
        self.rotate_angle = 0
        old_img_path = getattr(self, "imgPath").get()
        if not self.img_list:
            return
        elif old_img_path not in self.img_list:
            index = -1
        else:
            index = self.img_list.index(old_img_path)

        if index == len(self.img_list) - 1:
            return
        else:
            new_music_path = self.img_list[index + 1]
            getattr(self, "imgPath").set(new_music_path)
            self.img_show()

    # 逆时针旋转图片
    def rotate_img_button_callback(self, event=None):
        # 逆时针旋转90度
        self.rotate_angle += 90
        # 超过360度取余
        self.rotate_angle %= 360
        self.img_show()

    # 关闭当前的图片，并释放图片内存
    def close_img_button_callback(self, event=None):
        self.cancel_img()
        self.rotate_angle = 0

    # 拖动图片大小滑动条时，显示图片大小百分比
    def set_img_size_info(self, event=None):
        self.img_width = int(self.__dict__["imgSizeScale"].get() * self.img_max_width / 100)
        self.__dict__["imgSizeInfo"].set(str(self.img_width * 100 // self.img_max_width) + "%")

    # 设置当前显示的图片的大小，保持横纵比缩放
    def set_img_width(self, event=None):
        self.set_img_size_info()
        self.img_show()

    # 静态图片显示
    def default_img_show(self, img_path):
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

        out = img_data.resize((x_s, y_s), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(out)
        self.__dict__["imgLabel"].configure(image=self.img)

    # 加密静态图片显示
    def crypto_img_show(self, img_path):
        img_file_like = io.BytesIO(ByteCrypto(self.__dict__["password"].get()).decrypt(img_path))
        self.default_img_show(img_file_like)

    # 动态图片显示
    def default_gif_show(self, img_path):
        # 建立gif动图处理类
        self.gif = GifHandle(self.__dict__["imgLabel"], img_path)
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
        self.cancel_img()
        crypto_option = self.__dict__["cryptoOption"].get()
        img_path = self.__dict__["imgPath"].get()
        # 如果路径不存在或图片后缀不支持，则直接返回
        if not img_path or not os.path.exists(img_path) or os.path.splitext(img_path.lower())[1] not in self.img_ext:
            return
        img_name = os.path.basename(img_path)
        if crypto_option == "解密文件":
            decrypt_img_name = StringCrypto(self.__dict__["password"].get()).decrypt(img_name)
            if os.path.splitext(decrypt_img_name)[1] == ".gif":
                self.crypto_gif_show(img_path)
            else:
                self.crypto_img_show(img_path)
        elif crypto_option == "不需解密":
            if os.path.splitext(img_path)[1] == ".gif":
                self.default_gif_show(img_path)
            else:
                self.default_img_show(img_path)
        elif crypto_option == "解密保名":
            if os.path.splitext(img_path)[1] == ".gif":
                self.crypto_gif_show(img_path)
            else:
                self.crypto_img_show(img_path)


if __name__ == '__main__':
    app = Window("ImgLookUI.json")
    # 设置窗口标题:
    app.master.title("图片查看器")
    app.master.minsize(600, 150)
    # 主消息循环:
    app.mainloop()
