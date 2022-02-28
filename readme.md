# AUTOMATED SCORE FOLLOWING VIDEO BUILDER: 
### relies on pre-generated audio files and XML or LY.

N.B. Mac only but you could adapt the command line elements and run it on Windows

""" 
FIRST THINGS FIRST:
1) GENERATE YOUR SCORES AND EXPORT AS XML IN BACH (OR OTHER SOURCE METHOD)
2) USE MUSESCORE BATCH EXPORT TO CONVERT TO MP3 [SAVED ME FIGURING OUT TWO HARD STEPS] [download here](https://musescore.org/en/project/batch-convert#:~:text=This%20Plugin%20for%20MuseScore%20will,creates%20PDF%20versions%20of%20all%20%22%20.)
    P.S. If you have a lot of XML files to do, download an auto-clicker so that you can leave that rendering. 
3) Update XMLDIR and AUDIO_SOURCE_PATH
4) MAKE SURE ALL DEPENDANCIES ARE INSTALLED (see below - including everything used in shell). 
4b) You should run the script in a virtual environment if possible
5) Then you're safe to run the script!
"""

What you should know:
1:
- Converts all MusicXML (.xml) files in the specified folder to .ly by using a shell command: musicxml FILENAME
- this is the equivalent of doing this in the command line alone (Unix): find . -name "*.xml" -exec musicxml2ly {} \;

2:
- Loops through all the temporary .ly files and adds the contents of another .ly file (located in /config) to the beginning of the file
- the added information is (a) a paper size, which can be user-modified and (b) a copy of the lilypond library SVG-metadata written by Mathieu Demange (c) a message asking for the .ly file to be outputted as SVG by default rather than PDF
- the SVG-metadata is the really important bit as it provides a way to calculate how long the MIDI performance of each SVG page lasts

3:
- Each time a ly file is modified above, another function is called and the Ly file are written as a bunch of SVGs (one file per page), using the shell command: lilypond  -s -osvg_output FILENAME
- The ly files are deleted
- an "ImageClip" needs to be created using moviepy for each SVG file (i.e. one clip per page), the length of the clip is calculated using an SVG attribute called "data-time-end" (a non-standard attribute that is created by the wonderful SVG-metadata script) 
- before making the ImageClip, the SVG must be converted to PNG, which is done using cairosvg, When the clip is made, the SVG and PNG files are deleted.
- Each ImageClip derived from this source xml file is concatenated using moviepy and joined to the pre-made MIDI MP3. the SVG metadata means that pageturns should sync perfectly with the audio. The video file is rendered as an MP4 (H264) but other codecs can be selected depending on your system.

4:
- Each video file is saved in the /vids directory. The concatenation of all these files is NOT done with Moviepy as it accesses files frame by frame, which is unnecessary as video files can be joined very quickly if they are in exactly the same format. The script again uses a shell command, this time in ffmpeg: find *.mp4 | sed 's:\ :\\\ :g'| sed 's/^/file /' > fl.txt; ffmpeg -f concat -i fl.txt -c copy shell_concat_output.mp4; rm fl.txt"
- this command writes the names of all the .mp4 folder in the working directory (which has just been changed to the /vids folder) to a text fukem then runs the ffmpeg command "ffmpeg -f concat -i fl.txt -c copy shell_concat_output.mp4", then deletes the text file.

Dependencies: os, xml.dom, moviepy, cairosvg, reportlab.graphics
Shell dependencies: ffmpeg, lilypond/ly, musicxml2ly (which should be installed along with lilypond)

N.B. if you want to start with LY files, just comment out the call to batch_xml2ly and put your .ly files in the LY_DIR folder (be warned: they will be deleted)