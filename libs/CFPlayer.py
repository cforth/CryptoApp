import pyglet
import os


def play(video_path):
    if not os.path.exists(video_path):
        raise ValueError('Video path not exists: %s', video_path)

    player = pyglet.media.Player()
    source = pyglet.media.load(video_path)
    v_format = source.video_format
    window = pyglet.window.Window(width=v_format.width, height=v_format.height)
    player.queue(source)
    player.play()

    @window.event
    def on_draw():
        window.clear()
        player.get_texture().blit(0, 0)

    pyglet.app.run()
