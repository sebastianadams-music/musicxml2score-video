# AUTOMATED SCORE FOLLOWING VIDEO BUILDER: relies on pre-generated audio files and XML or LY.
""" 
FIRST THINGS FIRST:
1) GENERATE YOUR SCORES AND EXPORT AS XML IN BACH (OR OTHER SOURCE METHOD), AND READ THE README.MD
2) USE MUSESCORE BATCH EXPORT TO CONVERT TO MP3 [SAVED ME FIGURING OUT TWO HARD STEPS] 
    P.S. Download an auto-clicker so that you can leave that rendering.
"""

import os #the patch runs a couple of terminal commands, plus accesses files
from xml.dom import minidom
from moviepy.editor import *
import cairosvg
from reportlab.graphics import renderPM

'''PERSONAL PATHS AND QUALITY PARAMETERS'''
#XMLDIR = "/Users/sebastianadams/Dropbox/max_patches/BachProject2022/xmlexports/sinestudies/xml" 
XMLDIR = "/Users/sebastianadams/Dropbox/Mac/Documents/VSCodeProjects/musicxml2score-video/xml_test_files" #test batch of files. Comment out when happy
AUDIO_SOURCE_PATH = "/Users/sebastianadams/Dropbox/max_patches/BachProject2022/xmlexports/sinestudies/mp3"
FPS = 4 #increase for better but slower results
DPI = 150 #increase for better but slower results

'''DON'T CHANGE THESE'''
LYDIR = os.path.abspath("ly_tmp/")
SVGOUTPUT = os.path.abspath("svg_output") #SVG & PNG temp files go here 
VIDS = os.path.abspath("vids") #video output [BTW: temporary videos are kept]
CONFIG_FILE_PATH = os.path.abspath("config/SVG-metadata.ly")
CONFIG_FILE = f'\include "{CONFIG_FILE_PATH}"' # links to a file which includes Lilypond SVG-metadata library 

def main():
    os.system("echo Hello from the other side!")
    batch_xml2ly(XMLDIR)
    batch_prepend(LYDIR) 
    concat_movies_shell(VIDS)

    os.system("echo WE are DONE!")

def batch_xml2ly(dir):
    for root, dirs, files in os.walk(dir):
        for file in sorted(files):
            if file.endswith(".xml"):
                file = dir + "/" + file
                execute = f"cd {LYDIR}; musicxml2ly {file}"
                os.system(execute)

def batch_prepend(dir):
    for root, dirs, files in os.walk(dir):
        
        for file in sorted(files):
            
                if file.endswith(".ly"):
                    file_name = file
                    file = dir + "/" + file
                    line_prepender(file, CONFIG_FILE) #adds config info (link to a file containing SVG-metadata library + page size) to a lilypond file

                    # executes the command to create lilypond files in the terminal, with the silent flag and in the svg_output folder 
                    exec_ly = f'cd {SVGOUTPUT}; lilypond  -s -osvg_output {file}'
                    print(f"file {file} conveted to ly")
                    os.system(exec_ly)
                    print("file done: {file}")
                    os.remove(file)
                    
                    batch_SVG(SVGOUTPUT, file_name) #calls batch_SVG every time a .ly file is rendered 
                if file.endswith(".ly~"):  
                    os.remove(f"{LYDIR}/{file}")

def batch_SVG(dir, filename):
    for root, dirs, files in os.walk(dir):
        
        clip_array = []
        video_length = 0
        file_name = filename
        for file in sorted(files):
                file_name = file_name.replace(".ly", ".mp4")

                if file.endswith(".svg"):
                    file = dir + "/" + file
                    svg_length = get_svg_data(file) #extracts each data-time-end attribute from an SVG and returns the highest result
                    print("len: ", svg_length)
                    png_file = f"{SVGOUTPUT}out_png.png"
                    png = cairosvg.svg2png(url=file, dpi=DPI, background_color="white", write_to=png_file)
                    os.remove(file) #deletes the SVG file once it is written to a PNG
                    # PNG is rendered as moviepy imageclip with length (duration - previous length)
                    file = png_file
                    ic = ImageClip(file, transparent=False).set_duration(svg_length - video_length) 
                    video_length = svg_length #sets video_length to duration of current svg
                    #ic.write_videofile("test.mp4", fps=24, codec="libx264" ###test mp4 for troubleshooting what you're actually writing to the clip
                    clip_array.append(ic)
                    os.remove(file) #deletes the PNG file when done working with it
        print(clip_array)
        video = concatenate(clip_array, method="compose")
        audio_file_name = file_name[:-4] + ".mp3"
        audio_file_path = f"{AUDIO_SOURCE_PATH}/{audio_file_name}"
        video.write_videofile(f"{VIDS}/{file_name}", audio=audio_file_path, fps=FPS, codec="h264_videotoolbox")


def concat_movies_shell(dir): #outputs a joined video into the VIDS directory
    command = f"cd {dir}; find *.mp4 | sed 's:\ :\\\ :g'| sed 's/^/file /' > fl.txt; ffmpeg -f concat -i fl.txt -c copy shell_concat_output.mp4; rm fl.txt"
    os.system(command)

def line_prepender(filename, line):  # general purpose function which will prepend any one-line text to the start of a text file

    with open(filename, 'r+') as f:
        print(f)
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

def get_svg_data(svg_file): # should probably split this function out to make it generic 

    doc = minidom.parse(svg_file)  # calls an SVG file as an XML [if it crashes here, make sure svg folder is empty]
    x = 0
    time_end = float(0)
    for g in doc.getElementsByTagName('g'): # gets all gs
        x = (g.getAttribute("data-time-end"))
        x.replace(" ", "") #parses output to remove spaces
        
        if x: #empty strings are false so excluded here
            x = float(x)
            if x > time_end:
                time_end = x
    doc.unlink()
    return time_end


if __name__ == '__main__':
    main()