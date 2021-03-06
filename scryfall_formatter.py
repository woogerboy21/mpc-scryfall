import scrython
import imageio
import requests
import time
import config
import numpy as np
from numpy.fft import fft2, ifft2, fftshift, ifftshift
from skimage.transform import resize


def process_card(cardname):
    time.sleep(0.05)

    # If the card specifies which set to retrieve the scan from, do that
    try:
        pipe_idx = cardname.index("|")
        query = cardname[0:pipe_idx] + " set=" + cardname[pipe_idx+1:]
        card = scrython.cards.Search(q=query).data()[0]
        print("Processing: " + cardname + ", set: " + cardname[pipe_idx+1:])
    except (ValueError, scrython.foundation.ScryfallError):
        card = scrython.cards.Named(fuzzy=cardname).scryfallJson
        print("Processing: " + cardname)

    cardname = card["name"].replace("//", "&")  # should work on macOS & windows now
    r = requests.post(
        "https://api.deepai.org/api/waifu2x",
        data={
            'image': card["image_uris"]['large'],
        },
        headers={'api-key': config.TOKEN}
    )
    output_url = r.json()['output_url']
    im = imageio.imread(output_url)

    # Read in filter image
    filterimage = np.copy(imageio.imread("./filterimagenew.png"))

    # Resize filter to shape of input image
    filterimage = resize(filterimage, [im.shape[0], im.shape[1]], anti_aliasing=True, mode="edge")

    # Initialise arrays
    im_filtered = np.zeros(im.shape, dtype=np.complex_)
    im_recon = np.zeros(im.shape, dtype=np.float_)

    # Apply filter to each RGB channel individually
    for i in range(0, 3):
        im_filtered[:, :, i] = np.multiply(fftshift(fft2(im[:, :, i])), filterimage)
        im_recon[:, :, i] = ifft2(ifftshift(im_filtered[:, :, i])).real

    # Scale between 0 and 255 for uint8
    minval = np.min(im_recon)
    maxval = np.max(im_recon)
    im_recon_sc = (255 * ((im_recon - minval) / (maxval - minval))).astype(np.uint8)

    # TODO: pre-m15, post-8ed cards
    # TODO: pre-8ed cards (?)

    # Borderify image
    pad = 57  # Pad image by 1/8th of inch on each edge
    bordertol = 16  # Overfill onto existing border by 16px to remove white corners
    im_padded = np.zeros([im.shape[0] + 2 * pad, im.shape[1] + 2 * pad, 3])

    # Get border colour from left side of image
    bordercolour = np.median(im_recon_sc[200:(im_recon_sc.shape[0] - 200), 0:bordertol], axis=(0, 1))

    # Pad image
    for i in range(0, 3):
        im_padded[pad:im.shape[0] + pad, pad:im.shape[1] + pad, i] = im_recon_sc[:, :, i]

    # Overfill onto existing border to remove white corners
    # Left
    im_padded[0:im_padded.shape[0],
              0:pad + bordertol, :] = bordercolour

    # Right
    im_padded[0:im_padded.shape[0],
              im_padded.shape[1] - (pad + bordertol):im_padded.shape[1], :] = bordercolour

    # Top
    im_padded[0:pad + bordertol,
              0:im_padded.shape[1], :] = bordercolour

    # Bottom
    im_padded[im_padded.shape[0] - (pad + bordertol):im_padded.shape[0],
              0:im_padded.shape[1], :] = bordercolour

    # Remove copyright line
    # print(card["power"])
    if card["frame"] == "2015":
        # Modern frame
        leftPix = 735
        rightPix = 1140
        topPix = 1550
        bottomPix = 1585

        # creatures have a shifted legal line
        try:
            power = card["power"]
            toughness = card["toughness"]
            topPix = 1580
            bottomPix = 1615
            # Creature card
        except KeyError:
            pass

        # planeswalkers have a shifted legal line too
        try:
            loyalty = card["loyalty"]
            topPix = 1580
            bottomPix = 1605
        except KeyError:
            pass

        im_padded[topPix:bottomPix, leftPix:rightPix, :] = bordercolour

    elif card["frame"] == "2003":
        # 8ED frame
        try:
            loyalty = card["loyalty"]
            leftPix = 300
            rightPix = 960
            topPix = 1570
            bottomPix = 1600
            im_padded[topPix:bottomPix, leftPix:rightPix, :] = bordercolour
        except KeyError:
            # TODO: Content aware fill?
            pass

    # Remove holostamp
    if card["frame"] == "2015" and (card["rarity"] == "rare" or card["rarity"] == "mythic"):
        # Need to remove holostamp
        # Define bounds of ellipse to fill with border colour
        leftE = 575
        rightE = 690
        topE = 1520
        bottomE = 1575

        cx = (leftE + rightE) / 2
        cy = (topE + bottomE) / 2

        h = (bottomE - topE) / 2
        w = (rightE - leftE) / 2

        for x in range(leftE, rightE + 1):
            for y in range(topE, bottomE + 1):
                # determine if point is in the holostamp area
                if pow(x - cx, 2) / pow(w, 2) + pow(y - cy, 2) / pow(h, 2) <= 1:
                    # point is inside ellipse
                    im_padded[y, x, :] = bordercolour

    # Write image to disk
    imageio.imwrite("formatted/" + cardname + ".png", im_padded.astype(np.uint8))


if __name__ == "__main__":
    # Loop through each card in cards.txt and scan em all
    with open('cards.txt', 'r') as fp:
        for cardname in fp:
            process_card(cardname)
