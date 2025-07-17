# test_tkinter.py
import tkinter as tk

print("Trying to launch Tkinter window...")

root = tk.Tk()
root.title("Test Window")
root.geometry("300x200")
tk.Label(root, text="If you see this, Tkinter works!").pack(pady=50)
root.mainloop()
