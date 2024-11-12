@echo off

set FONT_BOLD_PATH=D:/ig/frame add/front/AnonymousPro-Bold.ttf
set FONT_REGULAR_PATH=D:/ig/frame add/front/AnonymousPro-Regular.ttf

set INPUT_FOLDER=D:/ig/frame add/images
set OUTPUT_FOLDER=D:/ig/frame add/output_images

set FONT_BOLD_SIZE=3
set FONT_REGULAR_SIZE=2 
set BORDER_WIDTH=2    
set BOTTOM_BORDER_HEIGHT=9 

python add_text_to_image.py

echo Settings have been set. Press any key to continue...
pause
