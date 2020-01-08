from scryfall_formatter import *

# Scan every card in a set
page = 0
cardnames = []
more = True
expansion = input("Type the three-character set code for the set you want to scan: ")

# ensure we get every card from the set (multiple search result pages)
while more:
    time.sleep(0.1)
    cardset = scrython.cards.Search(q="set:" + expansion, page=page)
    more = cardset.has_more()
    cardnames = cardnames + [cardset.data()[x]["name"] + "|" + expansion for x in range(len(cardset.data()))]
    page += 1

for cardname in cardnames:
    process_card(cardname)
