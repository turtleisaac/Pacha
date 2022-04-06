from tkinter import ttk, TOP, TRUE, LEFT, W, E
from tkinter import filedialog
from tkinter import messagebox
from ttkthemes import ThemedTk
import os
from tkinter.ttk import *
from tkinter import *

from Patch import PatchCreator, PatchApplier

# Developed by Turtleisaac

root = ThemedTk(theme="breeze")
root.title('Pacha')
root.resizable(False, False)
root.geometry('350x150')

top_frame = ttk.Frame(root)
top_frame.pack(side=TOP, pady=1)

style = ttk.Style()
style.configure("Hyperlink.TLabel", foreground="blue")

label1 = ttk.Label(top_frame, text="Pacha", font='Helvetica 18 bold')
label2 = ttk.Label(top_frame, text="Created by Turtleisaac")


def create():
    filetypes = [
        ('NDS File', '*.nds *.srl')
    ]

    modified_in = filedialog.askopenfile(title='Select Modified ROM', filetypes=filetypes, mode='r')
    if modified_in is not None:
        modified_path = os.path.abspath(modified_in.name)
        modified_in.close()

        original_in = filedialog.askopenfile(title='Select Original ROM', filetypes=filetypes, mode='r')
        if original_in is not None:
            original_path = os.path.abspath(original_in.name)
            original_in.close()

            creator = PatchCreator(modified_path, original_path)
            creator.create()

            f_out = filedialog.asksaveasfile(title='Select Output File', mode='w', defaultextension=".pacha")
            if f_out is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            filepath_output = os.path.abspath(f_out.name)
            f_out.close()

            creator.pickle(filepath_output)
            messagebox.showinfo(title='Pacha Creator', message='Patch Creation Complete! Output can be found at:\n' +
                                                       filepath_output)


def apply():
    patch_filetype = [
        ('Pacha File', '*.pacha')
    ]

    rom_filetype = [
        ('NDS File', '*.nds *.srl')
    ]

    patch_in = filedialog.askopenfile(title='Select Patch File', filetypes=patch_filetype, mode='r')
    if patch_in is not None:
        patch_path = os.path.abspath(patch_in.name)
        patch_in.close()

        original_in = filedialog.askopenfile(title='Select Input ROM', filetypes=rom_filetype, mode='r')
        if original_in is not None:
            original_path = os.path.abspath(original_in.name)
            original_in.close()

            applier = PatchApplier(patch_path, original_path)
            applier.apply()

            f_out = filedialog.asksaveasfile(title='Select Output ROM', mode='w', defaultextension=".nds")
            if f_out is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            filepath_output = os.path.abspath(f_out.name)
            f_out.close()

            applier.write(filepath_output)
            messagebox.showinfo(title='Pacha Applier', message='Patch Apply Complete! Output can be found at:\n' +
                                                               filepath_output)


# open button
create_button = ttk.Button(
    top_frame,
    text='Create Patch',
    command=create,
    width=30,
    # font='Helvetica 12 bold'
)

apply_button = ttk.Button(
    top_frame,
    text='Apply Patch',
    command=apply,
    width=30,
    # font='Helvetica 12 bold'
)

label1.grid(row=0, column=0, columnspan=2)
create_button.grid(row=1, column=0, columnspan=2, pady=5)
apply_button.grid(row=2, column=0, columnspan=2, pady=5)
label2.grid(row=3, column=0, columnspan=2)
top_frame.columnconfigure(0, weight=5, uniform='row')
top_frame.columnconfigure(1, weight=7, uniform='row')

root.eval('tk::PlaceWindow . center')

root.mainloop()
