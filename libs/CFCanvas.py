import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk


def get_screen_size(window):
    return window.winfo_screenwidth(), window.winfo_screenheight()


def get_window_size(window):
    return window.winfo_reqwidth(), window.winfo_reqheight()


def get_window_current_size(window):
    return window.winfo_width(), window.winfo_height()


def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (root.winfo_reqwidth(), root.winfo_reqheight(), (screenwidth-width)/2, (screenheight-height)/2)
    root.geometry(size)


# 读取图片，返回PIL.Image对象
def pil_image_read(img_path, rotate_angle, zoom_width):
    # 根据rotate_angle逆时针旋转图片
    if rotate_angle == 0 or rotate_angle == 180:
        img_data = Image.open(img_path).rotate(rotate_angle, expand=True)  # 旋转图像, 长宽调整
        x, y = img_data.size
        x_s = int(zoom_width)
        # 调整图片大小时保持横纵比
        y_s = int(y * x_s // x)
    elif rotate_angle == 90 or rotate_angle == 270:
        img_data = Image.open(img_path).rotate(rotate_angle, expand=True)  # 旋转图像, 长宽调整
        x, y = img_data.size
        y_s = int(zoom_width)
        # 调整图片大小时保持横纵比
        x_s = int(x * y_s // y)
    else:
        img_data = Image.open(img_path).rotate(rotate_angle)  # 旋转图像, 长宽不变
        x, y = img_data.size
        x_s = int(zoom_width)
        # 调整图片大小时保持横纵比
        y_s = int(y * x_s // x)

    return img_data.resize((x_s, y_s), Image.ANTIALIAS)


# GIF动图处理类
class GifHandle(object):
    def __init__(self, master_widget, img_path, rotate_angle=0):
        # 保存显示图片的控件引用
        self.master_widget = master_widget
        # 保存图片路径
        self.img_path = img_path
        # 逆时针旋转的角度
        self.rotate_angle = rotate_angle
        # 保存gif格式图片当前显示的帧的数据
        self._frame = None
        # 保存gif格式图片每一帧
        self._gif_frames = []
        # 保存gif格式图片帧的数量
        self._frame_count = 0
        # 保存gif格式图片每一帧的延时
        self.delay = 50
        # 保存gif格式图片当前显示的帧的位置
        self._ind = 0
        # 设置gif图片默认运行状态为关闭
        self._gif_running = False
        # 初始化gif动图
        self._init_gif()

    # 初始化GIF动图，将GIF动图每一帧保存起来准备显示
    def _init_gif(self):
        im = Image.open(self.img_path)
        seq = []
        try:
            while True:
                seq.append(im.copy())
                im.seek(len(seq))  # skip to next frame
        except EOFError:
            pass  # we're done
        try:
            self.delay = im.info['duration']
            # 将默认延时设置为50ms
            if self.delay < 50:
                self.delay = 50
        except KeyError:
            self.delay = 50
        first = seq[0].convert('RGBA')
        # 根据角度逆时针旋转图片
        self._gif_frames = [ImageTk.PhotoImage(first.rotate(self.rotate_angle, expand=True))]
        temp = seq[0]
        for image in seq[1:]:
            temp.paste(image)
            frame = temp.convert('RGBA')
            # 根据角度逆时针旋转图片
            self._gif_frames.append(ImageTk.PhotoImage(frame.rotate(self.rotate_angle, expand=True)))
            self._frame_count += 1

    # 更新GIF动图的下一帧
    def _update_gif(self):
        self._frame = self._gif_frames[self._ind]
        self._ind += 1
        if self._ind >= self._frame_count:
            self._ind = 0
        # 将gif当前帧显示在widget容器中
        self.master_widget.gif_frame_show(self._frame)
        # 设置定时器，更新widget容器显示的gif帧
        self.master_widget.gif_timer = self.master_widget.after(self.delay, self._update_gif)

    # 启动GIF动图
    def start_gif(self):
        # 设置gif图片运行标志
        self._gif_running = True
        # 在widget容器中设置定时器
        self.master_widget.gif_timer = self.master_widget.after(0, self._update_gif)

    # 停止当前的GIF动图
    def stop_gif(self):
        if self._gif_running:
            # 停止定时器
            self.master_widget.after_cancel(self.master_widget.gif_timer)
            self._gif_running = False


# 窗口类
class CFCanvas(ttk.Frame):
    def __init__(self, default_width, default_height, master=None):
        super().__init__(master, padding=2)
        self.img_data = None
        self.gif_data = None
        self.img_widget = None
        self.img_position_x = 0
        self.img_position_y = 0
        self.canvas_img_id = None
        self.screenwidth, self.screenheight = get_screen_size(self)
        self.canvas_width, self.canvas_height = default_width, default_height
        self.img_width, self.img_height = default_width, default_height

        self.canvas = tk.Canvas(self, bg="black", width=self.canvas_width, height=self.canvas_height,
                                scrollregion=(0, 0, self.img_width, self.img_height))
        self.ysb = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.xsb = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.canvas['xscrollcommand'] = self.xsb.set
        self.canvas['yscrollcommand'] = self.ysb.set

        self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.ysb.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.xsb.grid(row=1, column=0, sticky=tk.E + tk.W)
        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def default_gif_show(self, img_path, rotate_angle):
        self.gif_data = GifHandle(self, img_path, rotate_angle)
        self.gif_data.start_gif()

    def gif_frame_show(self, img_data):
        self.img_widget = img_data
        self.img_center()

    # 清空图片显示
    def cancel_img(self):
        # 如果有GIF动图正在运行，则停止这个定时事件
        if self.gif_data:
            self.gif_data.stop_gif()
        self.gif_data = None
        self.img_data = None

    def img_show(self, img_data):
        self.img_data = img_data
        self.img_width, self.img_height = self.img_data.size
        self.img_adjust_size(self.img_width, self.img_height)

    def img_adjust_size(self, width, height):
        canvas_width, canvas_height = get_window_current_size(self.canvas)
        self.img_width, self.img_height = int(width), int(height)
        if self.img_width > canvas_width:
            if self.img_width <= self.screenwidth - 50:
                self.canvas.configure(width=self.img_width)
            else:
                self.canvas.configure(width=self.screenwidth)
        if self.img_height > canvas_height:
            if self.img_height <= self.screenheight - 50:
                self.canvas.configure(height=self.img_height)
            else:
                self.canvas.configure(height=self.screenheight)

        self.canvas.configure(scrollregion=(0, 0, self.img_width, self.img_height))
        self.img_widget = ImageTk.PhotoImage(self.img_data.resize((self.img_width, self.img_height), Image.ANTIALIAS))
        self.img_center()

    def img_center(self, event=None):
        canvas_width, canvas_height = get_window_current_size(self.canvas)
        if canvas_width == 1 and canvas_height == 1:
            return
        else:
            self.canvas_width, self.canvas_height = canvas_width, canvas_height

            if self.img_width > self.canvas_width:
                self.img_position_x = 0
            else:
                self.img_position_x = (self.canvas_width - self.img_width) / 2

            if self.img_height > self.canvas_height:
                self.img_position_y = 0
            else:
                self.img_position_y = (self.canvas_height - self.img_height) / 2

            if self.canvas_img_id:
                self.canvas.delete(self.canvas_img_id)
            if self.img_widget:
                self.canvas_img_id = self.canvas.create_image(self.img_position_x, self.img_position_y,
                                                              anchor=tk.NW, image=self.img_widget)

    # 静态图片显示
    def default_img_show(self, img_path, rotate_angle, zoom_width):
        self.img_show(pil_image_read(img_path, rotate_angle, zoom_width))

    # 双页静态图片显示
    def default_double_img_show(self, img_path, next_img_path, order_option, rotate_angle, zoom_width):
        current_out = pil_image_read(img_path, rotate_angle, zoom_width)
        next_out = pil_image_read(next_img_path, rotate_angle, zoom_width)
        current_x, current_y = current_out.size
        current_x_s = int(zoom_width)
        current_y_s = int(current_y * current_x_s // current_x)
        next_x, next_y = next_out.size
        next_x_s = int(zoom_width)
        next_y_s = int(next_y * next_x_s // next_x)
        # 将两张图片合并为一张图片
        to_image = Image.new('RGBA', (current_x_s + next_x_s, current_y_s if current_y_s > next_y_s else next_y_s))
        if order_option == "左开":
            to_image.paste(current_out, (0, 0))
            to_image.paste(next_out, (current_x_s, 0))
        elif order_option == "右开":
            to_image.paste(next_out, (0, 0))
            to_image.paste(current_out, (next_x_s, 0))
        self.img_data = to_image
        self.img_show(self.img_data)
