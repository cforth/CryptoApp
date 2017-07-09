import tkinter as tk
import MainWindow


def main():
    application = tk.Tk()
    application.title("CryptoConverter")
    MainWindow.Window(application)
    application.mainloop()

main()