from PIL import Image, ImageDraw, ImageFont


image = Image.open('note.jpg')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('arial.ttf', 70) if 'arial.ttf' else ImageFont.load_default()
color = (0, 0, 0)
draw.text((350, 900), 'Hello, World!', font=font, fill=color)
font = ImageFont.truetype('arial.ttf', 45) if 'arial.ttf' else ImageFont.load_default()
draw.text((1260, 810), '12-12-2004', font=font, fill=color)
font = ImageFont.truetype('arial.ttf', 70) if 'arial.ttf' else ImageFont.load_default()
draw.text((635, 570), 'Some details...', font=font, fill=color)
font = ImageFont.truetype('arial.ttf', 70) if 'arial.ttf' else ImageFont.load_default()
x_pos = 1120
positions = [
    (x_pos, 1500),
    (x_pos, 1650),
    (x_pos, 1790),
    (x_pos, 1930),
    (x_pos, 2050),
    (x_pos, 2150),
    (x_pos, 2250)
]

for position in positions:
    draw.text(position, '100,000 UGX', font=font, fill=color)






image.save('output.jpg')


