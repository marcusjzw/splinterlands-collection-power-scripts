import requests
from collections import defaultdict
import json

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# The API references cards in IDs, so get a dict that maps IDs to the 
# corresponding card name.
cardDetailsRaw = requests.get("https://game-api.splinterlands.com/cards/get_details")
cardDetails = cardDetailsRaw.json()

idNameDict = {}
for i in range(len(cardDetails)):
    idNameDict[int(cardDetails[i]['id'])] = cardDetails[i]['name'], cardDetails[i]['rarity']

# Now call the API to fetch all cards for rent right now
rentDetailsRaw = requests.get("https://game-api.splinterlands.com/market/for_rent_grouped")
rentDetails = rentDetailsRaw.json()

# Ignoring BCX prices since I'm a noob, make a dict with the key as the card name,
# and value as the lowest price + whether a card is gold or not and its edition (stored in a tuple).
# Price is given in DEC by the API.
# 
# Note to self: Tuples are accessed via [<int>] syntax again.

# This uses the idNameDict to swap out id for the real card name

idLowestPriceDict = {}
for i in range(len(rentDetails)):
    idLowestPriceDict[i] = (idNameDict[int(rentDetails[i]['card_detail_id'])][0], rentDetails[i]['card_detail_id'], rentDetails[i]['gold'], rentDetails[i]['edition'], idNameDict[int(rentDetails[i]['card_detail_id'])][1], rentDetails[i]['low_price'], rentDetails[i]['low_price_bcx'])


# DATA IS STORED AS:
# Key: an int (doesn't mean anything)
# Value: Tuple containing 7 values: Card name, Card ID, isGoldCard, Edition, Rarity, Current lowest price, current lowest price per BCX

# HOW TO READ EDITION INTEGERS:  0,1 = alpha/beta, 2 = promo 3 = reward (id <= 223 is smooth reward, id >= 224 is broken reward), 4 = untamed, 5 = dice, 6 = gladius (none released yet)
# HOW TO READ RARITY INTEGERS:  0/1 = common, 2 = rare, 3 = epic, 4 = legendary
# Now we should be able to calculate each card's collection power

# ignore low_price_bcx for now, revisit later

# Check edition first (base power = 5, 10, 15 or 20 depending on bucket)
# Then check if gold (x50, but x25 for chaos legion edition)
# Then check rarity (common to rare is x4 but rare to epic is x5, epic to legendary is x5)

collectionPowerDict = {}
for i in range(len(idLowestPriceDict)):
    collectionPower = 0

    # EDITION LOGIC
    if (idLowestPriceDict[i][3] == 0 or idLowestPriceDict[i][3] == 2): # If edition is alpha/promo, base collection power is 30
        collectionPower = 30
    elif(idLowestPriceDict[i][3] == 1 or (idLowestPriceDict[i][3] == 3 and idLowestPriceDict[i][1] < 224)): # If edition is beta or (smooth) reward, base collection power is 15. Smooth reward is card id < 224
        collectionPower = 15
    elif(idLowestPriceDict[i][3] == 4 or idLowestPriceDict[i][3] == 5 or (idLowestPriceDict[i][3] == 3 and idLowestPriceDict[i][1] >= 224 and idLowestPriceDict[i][1] < 331)): # If edition is dice, untamed or (broken) reward, base collection power is 10. Broken reward is card id >= 224 but less than 331.
        collectionPower = 10
    elif(idLowestPriceDict[i][3] == 6 or (idLowestPriceDict[i][3] == 3 and idLowestPriceDict[i][1] >= 331)): # If edition is reward (chaos legion), base collection power is 5.
        collectionPower = 5

    # GOLD LOGIC 
    if (idLowestPriceDict[i][2]):
        if (idLowestPriceDict[i][3] == 3):
            collectionPower *= 25  # chaos legion gold cards will only *25 collection power
        else:
            collectionPower *= 50
    
    # RARITY LOGIC
    if (idLowestPriceDict[i][4] == 2): 
        collectionPower *= 4 # if it's a rare card, collection power x4 from common
    elif(idLowestPriceDict[i][4] == 3): 
        collectionPower *= 20 # if it's an epic card, collection power is x5 from rare
    elif(idLowestPriceDict[i][4] == 4):
        collectionPower *= 100 # if it's a legendary card, collection power is x5 from epic
    
    collectionPowerDict[i] = {'Name': idLowestPriceDict[i][0], 'isGold': idLowestPriceDict[i][2], 'CollectionPower: ': collectionPower, 'LowestPriceInDEC': idLowestPriceDict[i][5], 'CollectionPowerPerDEC': round(collectionPower / idLowestPriceDict[i][5], 2)}

# print(collectionPowerDict)

# we want to sort by collection power attained per DEC and find the best deals at the top

collectionPowerDict = [(k, collectionPowerDict[k]) for k in sorted(collectionPowerDict, key=lambda x: collectionPowerDict[x]['CollectionPowerPerDEC'], reverse=False)]
jprint(collectionPowerDict)



