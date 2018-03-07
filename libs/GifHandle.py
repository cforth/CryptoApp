from PIL import Image, ImageTk


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
        self.master_widget.configure(image=self._frame)
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
