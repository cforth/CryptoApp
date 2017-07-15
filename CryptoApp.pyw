import tkinter as tk
import MainWindow


def main():
    application = tk.Tk()
    application.title("CF加密解密器")
    MainWindow.Window(application)
    application.mainloop()

main()