from PIL import Image
import os, time
import matplotlib.pyplot as plt

# -------------------------------------------
'''
input below
'''
# path name for the folder containing raw images
folder_path = '/Users/jerryjiang/Desktop/Leukemia Samples/duke_slide_1001'
# crop size array, [0] is x span, [1] is y span
crop_size = [450,450]
# path name for saving cropped images
save_path = '/Users/jerryjiang/Desktop/testcrop'
# format of the raw images in string, such as '.tiff' or '.png'
image_type = '.tiff'

'''
TODO:
- implement tkinter
- add a point after clicking to show where exactly it's clicked
- convert to actual app?
- add a pathway to restart/repeat/quit

'''

# -------------------------------------------
# function that crops image at every click
def select_loc(event):

    # create list for coordinate storage
    global locations, dot, box
    
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
    locations.append([(start_x + end_x)/2, (start_y + end_y)/2, start_x, start_y, end_x, end_y])

    # add new dot and box trace to the storage array
    dot.append(ax.plot([(start_x + end_x)/2], [(start_y + end_y)/2],'r.'))
    box.append(ax.plot([start_x,start_x,end_x,end_x,start_x],[start_y,end_y,end_y,start_y,start_y],'k:'))

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
        for location in locations:
            subnum += 1
            image_cropped = image.crop((location[2],location[3],location[4],location[5]))
            image_cropped.save(save_path + '/%s_%d.tiff' % (names.replace(image_type, ''),subnum), format='TIFF')
    else:
        return

def back(event):
    if event.key == 'z':
        # remove the most previous selected coordinate
        locations.pop()
        # remove the most previous dot and box
        removed_dot, = dot.pop()
        removed_box, = box.pop()
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

# get all file names in the folder path, remove .DS_Store, and sort names
list_of_names = os.listdir(folder_path)
try:
    list_of_names.remove(".DS_Store")
except:
    print("No .DS_Store")
list_of_names.sort()

for names in list_of_names:

    # ignore other docs in folder with incorrect format
    if not(names.endswith(image_type)):
        continue

    # create full raw image path names
    raw_image_path = folder_path + '/' + names

    # create list for storing selected locations, dot traces, box traces
    locations = []
    dot = []
    box = []

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

    