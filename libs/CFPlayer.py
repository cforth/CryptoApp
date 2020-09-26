import pyglet
import os


def play(video_path):
    if not os.path.exists(video_path):
        raise ValueError('Video path not exists: %s', video_path)

    player = pyglet.media.Player()
    try:
        media_load = pyglet.media.load(video_path)
        v_format = media_load.video_format
        window = pyglet.window.Window(width=v_format.width, height=v_format.height)
        player.queue(media_load)
        player.play()

        @window.event
        def on_draw():
            window.clear()
            if player.source and player.source.video_format:
                player.get_texture().blit(0, 0)

    except Exception as e:
        print('CFPlayer Error:', e)

    pyglet.app.run()
