import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
from tkinter import filedialog

from PIL import Image
import os, time
import matplotlib.pyplot as plt

class CroppingTask:

    def __init__(self, title = 'Image Cropper', geometry = '900x400', resizable_x = True, resizable_y = True):

        # root window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(geometry)
        self.root.resizable(resizable_x, resizable_y)     

        # frame
        self.frame = ttk.Frame(self.root)

        def select_raw_images():
            filetypes = (('target image format', '*%s' % self.image_format.get()), ('All files', '*.*'))
            self.raw_images_path = filedialog.askopenfilenames(filetypes = filetypes)
            self.raw_images_path_label.set('Selected raw images: \n' + tuple_display(self.raw_images_path))
            # showinfo(title='Selected File', message=filename)

        def select_save_path():
            self.save_path = filedialog.askdirectory()
            self.save_path_path_label.set('Selected save path: \n' + self.save_path)

        def tuple_display(string_tuple):
            display_string = ''
            for i in range(len(string_tuple)):
                display_string += string_tuple[i]
                if i != len(string_tuple) - 1:
                    display_string += '\n'
            return display_string

        def save_crop_dimension():
            self.crop_dimension = (int(float(self.crop_dimension_x.get())),int(float(self.crop_dimension_y.get())))
            self.crop_dimension_display.set('Selected crop dimension: %s * %d' % self.crop_dimension)

        def crop_main():

            # -------------------------------------------

            # path name for the folder containing raw images
            list_of_names = list(self.raw_images_path)
            list_of_names.sort()
            # crop size array, [0] is x span, [1] is y span
            crop_size = self.crop_dimension
            # path name for saving cropped images
            save_path = self.save_path
            # format of the raw images in string, such as '.tiff' or '.png'
            image_type = self.image_format.get()

            # -------------------------------------------
            # function that crops image at every click
            def select_loc(event):
                
                image = Image.open(raw_image_path)

                # calculate cropping coordinates
                start_x = max(event.xdata - crop_size[0]/2,0)  # making sure start positions are nonnegative
                start_y = max(event.ydata - crop_size[1]/2,0)
                end_x = start_x + crop_size[0]
                end_y = start_y + crop_size[1]
                if end_x > image.size[0]:  # making sure end positions are not exceeding image boundaries
                    end_x = image.size[0]
                    start_x = end_x - crop_size[0]
                if end_y > image.size[1]:
                    end_y = image.size[1]
                    start_y = end_y - crop_size[1]
                
                # store center and corner coordinates into locations array
                self.locations.append([(start_x + end_x)/2, (start_y + end_y)/2, start_x, start_y, end_x, end_y])

                # add new dot and box trace to the storage array
                self.dot.append(ax.plot([(start_x + end_x)/2], [(start_y + end_y)/2],'r.'))
                self.box.append(ax.plot([start_x,start_x,end_x,end_x,start_x],[start_y,end_y,end_y,start_y,start_y],'k:'))

                # update canvas
                fig.canvas.draw()

                return

            def execute_crop(event):
                if event.key == 'enter':
                    # create image object
                    image = Image.open(raw_image_path)
                    # create sub index for cropped images saving
                    subnum = 0
                    # crop image and save
                    for location in self.locations:
                        subnum += 1
                        image_cropped = image.crop((location[2],location[3],location[4],location[5]))
                        image_cropped.save(save_path + '/%s_%d%s' % (names.replace(image_type, ''), subnum, image_type))
                else:
                    return

            def back(event):
                if event.key == 'z':
                    # remove the most previous selected coordinate
                    self.locations.pop()
                    # remove the most previous dot and box
                    removed_dot, = self.dot.pop()
                    removed_box, = self.box.pop()
                    removed_dot.remove()
                    removed_box.remove()
                    # update canvas
                    fig.canvas.draw()
                else:
                    return

            # go to next image when pressing 'q'
            def close_image(event):
                if event.key == 'q':
                    plt.close(fig)
                else:
                    return

            for raw_image_path in list_of_names:

                # remove the folder names and only take the last bit
                names = raw_image_path.split("/")[-1]

                # ignore other docs in folder with incorrect format
                if not(names.endswith(image_type)):
                    continue

                # create list for storing selected locations, dot traces, box traces
                self.locations = []
                self.dot = []
                self.box = []

                # matplotlib read image
                image = plt.imread(raw_image_path)

                # set title as file name, set window size to 10*8 inches, add image to figure, remove axis
                fig, ax = plt.subplots()
                ax.set_title(names)
                fig.set_size_inches(10, 8)
                ax.imshow(image)
                ax.axis('off')
                
                # connect keyboard/trachpad activities to corresponding actions
                fig.canvas.mpl_connect('button_press_event', select_loc)
                fig.canvas.mpl_connect('key_press_event', execute_crop)
                fig.canvas.mpl_connect('key_press_event', back)
                fig.canvas.mpl_connect('key_press_event', close_image)

                plt.show()

        # image format lead
        self.image_format_lead = ttk.Label(self.frame, text='Enter the image format (.tiff; .png; ...):')
        self.image_format_lead.grid(column=0, row=0, sticky='W', padx=5, pady=5)
        self.image_format_lead.focus()

        # image format entry
        self.image_format = tk.StringVar()
        self.image_format_entry = ttk.Entry(self.frame, textvariable=self.image_format)
        self.image_format_entry.grid(column=1, row=0, sticky='W', padx=5, pady=5)
        self.image_format_entry.focus()

        # raw images lead
        self.raw_images_lead = ttk.Label(self.frame, text='Select the target raw images to crop:')
        self.raw_images_lead.grid(column=0, row=1, sticky='W', padx=5, pady=5)
        self.raw_images_lead.focus()

        # save path lead
        self.save_path_lead = ttk.Label(self.frame, text='Select the path for saving cropped images:')
        self.save_path_lead.grid(column=0, row=3, sticky='W', padx=5, pady=5)
        self.save_path_lead.focus()

        # raw images selection
        self.raw_images_selection = ttk.Button(self.frame, text='Select the raw images', command=select_raw_images)
        self.raw_images_selection.grid(column=1, row=1, sticky='W', padx=5, pady=5)
        self.raw_images_selection.focus()

        # save path selection
        self.save_path_selection = ttk.Button(self.frame, text='Select the save path', command=select_save_path)
        self.save_path_selection.grid(column=1, row=3, sticky='W', padx=5, pady=5)
        self.save_path_selection.focus()

        # display selected raw images
        self.raw_images_path_label = tk.StringVar()
        self.raw_images_path_label.set('Selected raw images:')
        self.raw_images_selected = ttk.Label(self.frame, textvariable=self.raw_images_path_label)
        self.raw_images_selected.grid(column=1, row=2, sticky='W', padx=5, pady=5, columnspan=2)
        self.raw_images_selected.focus()

        # display selected save path
        self.save_path_path_label = tk.StringVar()
        self.save_path_path_label.set('Selected save path:')
        self.save_path_selected = ttk.Label(self.frame, textvariable=self.save_path_path_label)
        self.save_path_selected.grid(column=1, row=4, sticky='W', padx=5, pady=5, columnspan=2)
        self.save_path_selected.focus()

        # choose crop dimension top text
        self.crop_dimension_top_text = ttk.Label(self.frame, text='Enter the crop dimension:')
        self.crop_dimension_top_text.grid(column=0, row=5, sticky='W', padx=5, pady=5)
        self.crop_dimension_top_text.focus()

        # choose crop dimension lead
        self.crop_dimension_x_lead = ttk.Label(self.frame, text='Horizontal (x-axis)')
        self.crop_dimension_x_lead.grid(column=1, row=5, sticky='W', padx=5, pady=5)
        self.crop_dimension_x_lead.focus()
        self.crop_dimension_y_lead = ttk.Label(self.frame, text='Vertical (y-axis)')
        self.crop_dimension_y_lead.grid(column=1, row=6, sticky='W', padx=5, pady=5)
        self.crop_dimension_y_lead.focus()

        # crop dimension entry
        self.crop_dimension_x = tk.StringVar()
        self.crop_dimension_x_entry = ttk.Entry(self.frame, textvariable=self.crop_dimension_x)
        self.crop_dimension_x_entry.grid(column=2, row=5, sticky='W', padx=5, pady=5)
        self.crop_dimension_x_entry.focus()
        self.crop_dimension_y = tk.StringVar()
        self.crop_dimension_y_entry = ttk.Entry(self.frame, textvariable=self.crop_dimension_y)
        self.crop_dimension_y_entry.grid(column=2, row=6, sticky='W', padx=5, pady=5)
        self.crop_dimension_y_entry.focus()

        # save crop dimension
        self.crop_dimension_save = ttk.Button(self.frame, text='Save crop dimension', command=save_crop_dimension)
        self.crop_dimension_save.grid(column=1, row=7, sticky='W', padx=5, pady=5)
        self.crop_dimension_save.focus()

        # display entered crop dimension
        self.crop_dimension_display = tk.StringVar()
        self.crop_dimension_display.set('Selected crop dimension:')
        self.crop_dimension_entered = ttk.Label(self.frame, textvariable=self.crop_dimension_display)
        self.crop_dimension_entered.grid(column=1, row=8, sticky='W', padx=5, pady=5, columnspan=2)
        self.crop_dimension_entered.focus()

        # start cropping
        self.start_croppping = ttk.Button(self.frame, text='Start Cropping', command=crop_main)
        self.start_croppping.grid(column=0, row=9, sticky='W', padx=5, pady=5)
        self.start_croppping.focus()

        self.frame.grid(padx=10, pady=10)

        self.root.mainloop()

    


if __name__ == "__main__":
    haha = CroppingTask()