import pyglet
import os


def play(video_path):
    if not os.path.exists(video_path):
        raise ValueError('Video path not exists: %s', video_path)

    player = pyglet.media.Player()
    try:
        media_load = pyglet.media.load(video_path)
        v_format = media_load.video_format
        window = pyglet.window.Window(width=v_format.width, height=v_format.height,
                                      caption="VideoPlayer", resizable=True)
        player.queue(media_load)
        player.play()

        @window.event
        def on_draw():
            window.clear()
            x_pos = (window.width - v_format.width) / 2
            y_pos = (window.height - v_format.height) / 2
            x_pos = x_pos if x_pos >= 0 else 0
            y_pos = y_pos if y_pos >= 0 else 0

            if player.source and player.source.video_format:
                player.get_texture().blit(x_pos, y_pos)

        @window.event
        def on_key_press(symbol, modifiers):
            # 空格暂停
            if symbol == 32:
                if player.playing:
                    player.pause()
                else:
                    player.play()

    except Exception as e:
        print('CFPlayer Error:', e)

    pyglet.app.run()