# mpc-scryfall
Simple tool to retrieve Scryfall scans of MTG cards, perform some light processing on them, and prepare them for printing with MPC. This tool will throw Scryfall scans through waifu2x (courtesy of deepAI), lightly filter the image, then remove the holographic stamp.

# Requirements
* An internet connection while the tool is running
* A deepAI.org account (free) 
* Python 3
* The Python 3 packages:
   * Scrython
   * imageio
   * requests
   * numpy
   * scikit-image

# Install / Usage Guide
* Download the script and filter image somewhere on your computer
* Create a file called `config.py` in the same folder. Its contents should be the line `TOKEN = '<your token from deepAI.org>'`, excluding the <>'s.
* Create a folder called `formatted` in the same location
* Create a text file called `cards.txt` and put the card names you want to scan in it, one on each line
* To scan each card in `cards.txt`, run `scryfall_formatter.py`
* To do entire sets at a time, run `scryfall_formatter_set.py` and type in the three-character set code for the set you want when prompted

# Limitations / Other Notes
This can work on any magic card scan, but it'll only attempt to do post-filtering cleanup on planeswalkers and any cards printed in the M15 onwards frame. I also haven't tried printing any cards yet with this, but I placed some of the resulting images into MPC and the crops looked fine.
