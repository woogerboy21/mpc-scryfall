from scryfall_formatter import *

# Scan every card in a cube
page = 0
cardnames = []
more = True
expansion = input("Type the character set code for the cube you want to scan: ")

# ensure we get every card from the cube (multiple search result pages)
while more:
    time.sleep(0.1)
    cardset = scrython.cards.Search(q="cube:" + expansion, page=page)
    more = cardset.has_more()
    cardnames = cardnames + [cardset.data()[x]["name"] for x in range(len(cardset.data()))]
    page += 1

print("Collected search results for cube: " + expansion)

for cardname in sorted(set(cardnames)):
    process_card(cardname, expansion=None)
