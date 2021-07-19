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
        # alternate the case of the content
        # perform the conversion over entire string
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

    msg_width = 0
    msg_list = []

    # add the fixed text (same for image and text)
    msg_list.append('Literally no one:')
    msg_list.append(name + ': ')

    # only get size of name, as this needs to be expanded


    name_offset = 0
    for c in msg_list[1]:
        name_offset += font_type.getsize(c)[0]


    # images do not have further text
    msg_width = name_offset
    if not isImage:
        img_width, _ = img_sp.size

        for c in msg:
            # keep margin to the right
            if msg_width > (img_width-8):
                msg_width = name_offset
                msg_list.append('')

            msg_list[-1] += c
            msg_width += font_type.getsize(c)[0]



    for idx, line in enumerate(msg_list):
        # first two lines have no left margin
        x_off = 0 if idx < 2 else name_offset

        draw.text(
            xy = (x_off, idx*30),
            text = line,
            fill = (0,0,0),
            font=font_type
        )


    if(isImage):
        # the image is spanning vertical over title and name column
        # the width of both must be known

        title_offset = 0
        for c in msg_list[0]:
            title_offset += font_type.getsize(c)[0]

        x_offset = title_offset if title_offset > name_offset else name_offset
        offset = x_offset + 10, 10 # top, left margin 10

        mock_image = Image.open(src_image_buff)

        img_width, _ = img_sp.size
        mock_width, mock_height = mock_image.size

        # get the maximum width (either mocked image or max. space usage)
        allowed_width = img_width - offset[0] - 10 # right margin of 10
        eff_width = allowed_width if allowed_width < mock_width else mock_width


        allowed_height = 110 # space is 125, but top margin is 10, bottom margin is 5
        eff_height = allowed_height if allowed_height < mock_height else mock_height


        size = eff_width, eff_height
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
        try:
            await message.channel.send(file=discord.File(fp=output, filename='mock_{:s}_{:s}.png'.format(name, rand_suffix)))
        except discord.Forbidden:
            return False

    return True
