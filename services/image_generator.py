from PIL import Image, ImageDraw, ImageFont
import os


def generate_tickerbot_image(text):
  #   text = ''' Symbol |          Company        | Price | %Change
  #
  # AAPL  |  Apple Inc.             | $0.00 |   0.00%
  # META  |  Meta Platforms, Inc.   | $0.00 |   2.00%
  # MSFT  |  Microsoft Corporation  | $0.00 |  -2.00%'''
    pipe_indices = [i + 1 for i, char in enumerate(text.split('\n')[0]) if char == '|']

    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, 'RedditMono-Regular.ttf')
    font_path = os.path.normpath(font_path)
    font_size = 36
    font = ImageFont.truetype(font_path, font_size)

    # calculate height and width that the image needs to be to fit all the text @ font_size
    dummy_image = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    bbox = draw.multiline_textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    image_width = text_width + 40
    image_height = text_height + 40

    # draw text box of values
    image = Image.new('RGB', (image_width, image_height), color='#313338')
    draw = ImageDraw.Draw(image)

    # draw vertical lines on image
    text_len = len(text.split('\n')[0])
    percent_of_line = [pipe / text_len for pipe in pipe_indices]
    x_index = [percent * text_width for percent in percent_of_line]
    for x in x_index:
        draw.line([(x, 0), (x, image_height)], fill='white', width=1)

    # draw horizontal line on image
    text_rows = len(text.split('\n'))
    percent_of_height = 2 / text_rows
    y_index = percent_of_height * text_height
    draw.line([(0, y_index), (image_width, y_index)], fill='white', width=1)

    y = 20
    spacing = draw.textbbox((0, 0), "A", font)[3] + 4
    for line in text.split('\n'):
        x = 20
        line_bbox = draw.textbbox((0, 0), line, font=font)
        for word in line.split('|'):
            word += ' '
            line_bbox = draw.textbbox((0, 0), word, font=font)
            if '%' in word:
                if 'Change' in word or ' 0.00' in word:
                    color = 'white'
                elif '-' in word:
                    color = 'red'
                else:
                    color = 'green'
            else:
                color = 'white'
            draw.text((x, y), word, fill=color, font=font)
            x += line_bbox[2] - line_bbox[0]
        y += spacing
    return image
    # image.save('test_image.png')

# previous method of generation:
################################
# pipe_indices = [i + 1 for i, char in enumerate(text.split('\n')[0]) if char == '|']
# text = text.replace('|', ' ')
#
# script_dir = os.path.dirname(os.path.abspath(__file__))
# font_path = os.path.join(script_dir, 'RedditMono-Regular.ttf')
# font_path = os.path.normpath(font_path)
# font_size = 36
# font = ImageFont.truetype(font_path, font_size)
#
# # calculate height and width that the image needs to be to fit all the text @ font_size
# dummy_image = Image.new('RGB', (1, 1))
# draw = ImageDraw.Draw(dummy_image)
# bbox = draw.multiline_textbbox((0, 0), text, font=font)
# text_width = bbox[2] - bbox[0]
# text_height = bbox[3] - bbox[1]
# image_width = text_width + 40
# image_height = text_height + 40
#
# # draw text box of values
# image = Image.new('RGB', (image_width, image_height), color='#36393e')
# draw = ImageDraw.Draw(image)
# draw.multiline_text((20, 20), text, fill="white", font=font)
#
# # draw vertical lines on image
# text_len = len(text.split('\n')[0])
# percent_of_line = [pipe / text_len for pipe in pipe_indices]
# x_index = [percent * text_width for percent in percent_of_line]
# for x in x_index:
#     draw.line([(x, 0), (x, image_height)], fill='white', width=1)
#
# # draw horizontal line on image
# text_rows = len(text.split('\n'))
# percent_of_height = 2 / text_rows
# y_index = percent_of_height * text_height
# draw.line([(0, y_index), (image_width, y_index)], fill='white', width=1)
# image.save('good_image.png')