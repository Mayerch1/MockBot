import os
import io
import uuid
from PIL import Image, ImageDraw, ImageFont

import discord

async def perform_sponge(message, res_dir, sp_source):
    """perform the spongebob mocking on a message
       function does generate image with mocking text and send to messages channel
       Does NOT delete 'message' by itself

    Arguments:
        message {discord.Message} -- target message, contains channel information
        res_dir {str} -- contains resources (used fonts)
        sp_source {str} -- path to sponge image
    """
    # in case the message was an image
    # download the image to the disk
    if message.content == '':
        
        if not message.attachments:
            # neither image nor string content
            # -> embeds (links) are not supported
            return False

        isImage = True

        src_image_buff = io.BytesIO()
        await message.attachments[0].save(fp=src_image_buff)

    else:
        isImage = False

        # make every second letter upper
        # make every other second lower
        upper = message.content.upper()
        lower = message.content.lower()
        msg = ''

        for i in range(0, len(message.content)):
            if (i%2) :
                msg += lower[i]
            else:
                msg += upper[i]


    ############################
    #############################


    name = message.author.display_name
    

    # open image and create font
    img_sp = Image.open(res_dir + '/' + sp_source)
    font_type = ImageFont.truetype(res_dir + '/comicSans.ttf', 20)
    draw = ImageDraw.Draw(img_sp)

    # get size of the username on the image
    name_width = 0
    for c in name:
        name_width += font_type.getsize(c)[0]


    msg_1 = msg_2 = msg_3 = ''
    # insert linebreak into message, if needed
    # break into max 3 lines, as there is no more space
    if (not isImage):                
        img_width, _ = img_sp.size
        msg_width = 0
        for c in msg:
            msg_width += font_type.getsize(c)[0]
            if msg_width <= img_width-8-name_width:
                msg_1 += c
            elif msg_width <= 2*(img_width-8-name_width):
                msg_2 += c                    
            else:
                msg_3 += c

    # write first line and name
    # draw for image and text
    draw.text(
        xy = (0,0),
        text='Literally no one:',
        fill=(0,0,0),
        font=font_type
    )
    draw.text(
        xy=(0,30),
        text=name + ':',
        fill=(0,0,0),
        font=font_type,
    )


    if(not isImage):
        # get length of message
        text_width_raw = 0
        for c in msg:
            text_width_raw += font_type.getsize(c)[0]

        # print text onto image
        draw.text(
            xy=(name_width + 8, 30),
            text=msg_1,
            fill=(0,0,0),
            font=font_type,
        )

        # draw 2nd line, will be empty if not needed
        draw.text(
            xy=(name_width + 8, 60),
            text=msg_2,
            fill=(0,0,0),
            font=font_type,
        )

        # draw 3rd line, if needed
        draw.text(
            xy=(name_width + 8, 90),
            text=msg_3,
            fill=(0,0,0),
            font=font_type,
        )

    elif(isImage==1):
        img_width, _ = img_sp.size

        mock_image = Image.open(src_image_buff)
                    
        offset = int(img_width/2), 10
        size = img_width-offset[0], 100
        mock_image.thumbnail(size, Image.ANTIALIAS)

        img_sp.paste(mock_image, offset)




    with io.BytesIO() as output:
        img_sp.save(output, format='PNG')
        output.seek(0)

        # to not confuse users with equal file names
        # they do not need to be unique from the technical side
        rand_suffix = str(uuid.uuid4())[-7:] 

        # filename is necessary to trigger discord render engine
        # permission ensured by caller
        await message.channel.send(file=discord.File(fp=output, filename='mock_{:s}_{:s}.png'.format(name, rand_suffix)))

    return True
