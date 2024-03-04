from shared_vars import allCards
async def cardNameRequest(requestName):
  maxWeight = 1
  maxWeightName = ""
  for cardName in allCards.keys():
    currentWeight = await similarity(cardName, requestName)
    if currentWeight > maxWeight:
      maxWeight = currentWeight
      maxWeightName = cardName
    elif currentWeight == maxWeight:
      if len(cardName) < len(maxWeightName):
        maxWeightName = cardName
  return maxWeightName


async def similarity(name, key):
  weight = 0
  for i in range(len(key)):
    for j in range(len(name)):
      for x in range(1, min( len(name) - j , len(key) - i ) + 1):
        if key[i:i+x] != name[j:j+x] or x == min( len(name) - j , len(key) - i ):
          weight += max((x-1) * (x-1) -1, 0)
          break
  if name == key or name + " " == key:
    weight = 10000000
  return weight

