def printList(myList):
  if len(myList) == 0:
    print("None")
  for item in range(len(myList)):
    print(myList[item])

def printDict(dictionary):
  if len(dictionary) == 0:
    print("None")
  for item in dictionary:
    print(item, ": ", str(dictionary.get(item)))

# def printTupleList(tupleList):
#   if len(tupleList) == 0:
#     print("None")
#   for tuple in tupleList:
#     print(tuple[0])
