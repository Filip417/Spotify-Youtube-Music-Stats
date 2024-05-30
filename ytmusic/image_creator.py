from PIL import Image, ImageDraw, ImageFont
import requests, ast, textwrap
from io import BytesIO
from django.contrib.staticfiles import finders

def get_image(name, top_tracks, top_artists, top_artist):
    # Default size is 900x1600 and all other dimensions/sizes are adjusted to it
    # Therefore recommended not to change or scale all other dimensions/sizes accordingly
    width = 900
    height = 1600
    image = Image.new('RGBA', (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(image)

    def draw_text(position, text, fill, style, size):
        font_path = finders.find(f"ytmusic/font/Inter-{style}.ttf")
        font = ImageFont.truetype(font_path, size)
        draw.text(position, text, fill=fill, font=font)

    def draw_image(position, img_url, size=None):
        response = requests.get(url=img_url)
        image_from_url = Image.open(BytesIO(response.content))
        
        if size:
            target_width, target_height = size
            original_width, original_height = image_from_url.size
            
            # Calculate the aspect ratio
            aspect_ratio = original_width / original_height
            target_aspect_ratio = target_width / target_height
            
            if aspect_ratio > target_aspect_ratio:
                # Image is wider than the target aspect ratio
                new_height = target_height
                new_width = int(new_height * aspect_ratio)
            else:
                # Image is taller than the target aspect ratio
                new_width = target_width
                new_height = int(new_width / aspect_ratio)
            
            # Resize the image with the new dimensions
            resized_image = image_from_url.resize((new_width, new_height), Image.LANCZOS)
            
            # Calculate the cropping box
            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = (new_width + target_width) / 2
            bottom = (new_height + target_height) / 2
            
            # Crop the image to the target size
            cropped_image = resized_image.crop((left, top, right, bottom))
            
            image_from_url = cropped_image
        
        # Paste the image onto the main image
        if image_from_url.mode == 'RGBA':
            image.paste(image_from_url, position, image_from_url)
        else:
            image.paste(image_from_url, position)
        

    def draw_gradient(start_color, end_color):
        for y in range(height):
                color = (
                    int(start_color[0] + (end_color[0] - start_color[0]) * y / height),
                    int(start_color[1] + (end_color[1] - start_color[1]) * y / height),
                    int(start_color[2] + (end_color[2] - start_color[2]) * y / height)
                )
                draw.line((0, y, width, y), fill=color)


    #Variables to adjust wrapping text function
    max_line_width = 15
    indentation = '     '
    max_item_characters = 45

    def wrap_text(text, width, indent=''):
        wrapped_lines = textwrap.wrap(text, width=width)
        return '\n'.join([wrapped_lines[0]] + [indent + line for line in wrapped_lines[1:]])
    

    # Set variables from input, ready for drawing
    top_artists_dict = ast.literal_eval(top_artists)
    top_5_artists = ''
    for index, artist in enumerate(top_artists_dict):
        artist_name = artist['artist'][:max_item_characters]
        wrapped_artist = wrap_text(artist_name, max_line_width, indentation)
        top_5_artists += f'{index+1}. {wrapped_artist}\n'
 
    top_tracks_dict = ast.literal_eval(top_tracks)
    top_5_tracks = ''
    for index, track in enumerate(top_tracks_dict):
        track_name = track['title'][:max_item_characters]
        wrapped_track = wrap_text(track_name, max_line_width, indentation)
        top_5_tracks += f'{index+1}. {wrapped_track}\n'

    top_artist_dict = ast.literal_eval(top_artist)
    top_artist_img_url = top_artist_dict['thumbnails'][-1]['url']   

    # Drawing functions executed
    draw_gradient((0,0,0),(24,24,24))

    draw_image((130,130), top_artist_img_url, (640,640))

    draw_text((100,870), 'Top Artists', (155, 155, 155), 'SemiBold', 32)
    draw_text((500,870), 'Top Songs', (155, 155, 155), 'SemiBold', 32)

    draw_text((100,920), top_5_artists, (255, 255, 255), 'Bold', 32)
    draw_text((500,920), top_5_tracks, (255, 255, 255), 'Bold', 32)

    draw_text((180,1520), f"@{name}", (255, 0, 0), 'SemiBold', 20)
    draw_image((100,1485),'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Youtube_Music_icon.svg/240px-Youtube_Music_icon.svg.png', (64,64))
    draw_text((180,1490), "YouTube Music summary", (155, 155, 155), 'SemiBold', 24)

    return image

