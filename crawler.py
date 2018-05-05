import requests, queue, sys, re, collections, time
from bs4 import BeautifulSoup

q = queue.Queue()
parsedLinks = {}
outgoingLinks = {}
disallowedLinks = {}
badLinks = []
graphicLinks = {}
processedLinks = []
duplicateContent = []
disallowedDirs = []
graphicExtensions = ["gif", "jpg", "jpeg", "png", "pdf", "xlsx"]
textExtensions = ["htm", "html", "txt", "php"]
startingLink = 'http://lyle.smu.edu/~fmoore/'
myUserAgent = "Kellen's Web Crawler 1.0"
headers = {
    "User-Agent": myUserAgent
}
documents = []
documentIndicies = []
index = {}
allWords = {}

# Functions

def readRobotsTxt():
  result = requests.get(startingLink + "robots.txt", headers=headers)
  plain = result.text
  
  uaIndex = plain.find("User-agent:")
  if uaIndex == -1:
    return
  
  allowedUserAgent = plain[uaIndex+12 : uaIndex+13]
  if allowedUserAgent != "*" and allowedUserAgent != myUserAgent:
    return
  
  disallowedIndex = plain.find("Disallow: ", uaIndex) + 10
  endDisallowedIndex = re.search(r"\s", plain[disallowedIndex:]).start() + disallowedIndex
  disallowedDirs.append(plain[disallowedIndex:endDisallowedIndex])

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

def printTupleList(tupleList):
  if len(tupleList) == 0:
    print("None")
  for tuple in tupleList:
    print(tuple[0])

def addToOutgoingLinks(newLink):
  if newLink in outgoingLinks:
    newCount = outgoingLinks.get(newLink) + 1
  else:
    newCount = 1
  
  outgoingLinks.update({newLink: newCount})

def addToParsedLinks(newLink):
  if newLink in parsedLinks:
    newCount = parsedLinks.get(newLink) + 1
  else:
    newCount = 1
  
  parsedLinks.update({newLink: newCount})

def addToDisallowedLinks(newLink):
  if newLink in disallowedLinks:
    newCount = disallowedLinks.get(newLink) + 1
  else:
    newCount = 1
  
  disallowedLinks.update({newLink: newCount})

def addToGraphicLinks(newLink):
  if newLink in graphicLinks:
    newCount = graphicLinks.get(newLink) + 1
  else:
    newCount = 1
  
  graphicLinks.update({newLink: newCount})

def addToAllWords(token):
  if token in allWords:
    newCount = allWords.get(token) + 1
  else:
    newCount = 1
  
  allWords.update({token: newCount})

def createTokensDict(list):
  newDict = {}
  for item in list:
    if item in newDict:
      newCount = newDict.get(item) + 1
    else:
      newCount = 1
    
    newDict.update({item: newCount})

  return newDict

def addtoQueue(newLink):
  if newLink not in parsedLinks:
    q.put(newLink)

def isRelativeLink(url):
  try:
    result = requests.get(startingLink + url, headers=headers)
    if result.status_code == 200:
      return True
    else:
      return False
  except Exception:
    return False

def isGraphicLink(url):
  lastDot = url.rfind('.')
  suffix = url[lastDot+1:]

  if suffix in graphicExtensions:
    return True
  else:
    return False

def isDisallowedDir(url):
  for dir in disallowedDirs:
    if re.search(dir, url) or re.search(dir, startingLink + url):
      return True

  return False

def removeNonwords(oldTokenList):
  newTokenList = []
  for token in oldTokenList:
    if(token[0:1].isalpha() and token[len(token) - 1:len(token)].isalnum()):
      newTokenList.append(token)

  return newTokenList

def diff(first, second):
  second = set(second)
  return [item for item in first if item not in second]

def processLink(url, linkIndex):
  if url in processedLinks:
    return

  processedLinks.append(url)

  if isDisallowedDir(url):
    addToDisallowedLinks(url)
    return

  try:
    code = requests.get(url, headers=headers)
  except Exception:
    if isRelativeLink(url):
      url = startingLink + url
      code = requests.get(url, headers=headers)
    else:
      badLinks.append(url)
      return

  if isGraphicLink(url):
    addToGraphicLinks(url)
    return

  if not re.search(r"https?://(lyle|s2).smu.edu/~fmoore", url):
    addToOutgoingLinks(url)
    return
    
  addToParsedLinks(url)
  plain = code.text
  s = BeautifulSoup(plain, "html.parser")
  
  stopwordsFile = ' '.join(sys.argv[2:])
  with open(stopwordsFile) as f:
    stopwords = f.read().splitlines()

  for link in s.find_all('a'):
    linkSrc = str(link.get('href'))
    addtoQueue(linkSrc)
  
  plainText = s.get_text().lower()
  duplicateTuplesList = [item for item in documents if item[1] == plainText]
  for tuple in duplicateTuplesList:
    duplicateContent.append((url, tuple[0]))
  if len(duplicateTuplesList) == 0:
    documents.append((url, plainText))
    
  unfilteredTokens = plainText.split()
  withoutNonwords = removeNonwords(unfilteredTokens)
  filteredTokens = diff(withoutNonwords, stopwords)

  index.update({linkIndex: createTokensDict(filteredTokens)})
  documentIndicies.append(linkIndex)
  for token in filteredTokens:
    addToAllWords(token)

def getDocumentFreq(token):
  freq = 0
  for docIndex in documentIndicies:
    if index.get(docIndex).get(token):
      freq = freq + 1
  return freq

def printMatrix():
  print("Term-Document Frequency Matrix")
  print("Word\t\t\t\t\t\t", end="")
  for docIndex in documentIndicies:
    print("Doc #", docIndex, sep="", end="\t")
  for word in allWords:
    print("\n", word, sep="", end='\t')
    if len(word) < 8:
      print("", end="\t\t\t\t\t")
    elif len(word) < 16:
      print("", end="\t\t\t\t")
    elif len(word) < 24:
      print("", end="\t\t\t")
    elif len(word) < 32:
      print("", end="\t\t")
    elif len(word) < 40:
      print("", end="\t\t")
    for docIndex in documentIndicies:
      if index.get(docIndex).get(word):
        print(index.get(docIndex).get(word), end='\t')
      else:
        print("0", end='\t')

def printTopTwenty():
  print("\nTop 20 Tokens")
  print("Token\t\tCollectionFreq\tDocumentFreq")
  d = collections.Counter(allWords)
  d.most_common()
  for k, v in d.most_common(20):
    print(k, end="\t")
    if len(k) < 8:
      print("\t", end="")
    print(v, getDocumentFreq(k), sep="\t\t")

# Main

print("\n*************************************")
print("*       Kellen's Web Crawler        *")
print("*************************************\n")

maxNumLinks = int(sys.argv[1])
addtoQueue(startingLink)
addToParsedLinks(startingLink)
linkIndex = 0

readRobotsTxt()

while(not q.empty() and linkIndex < maxNumLinks):
  processLink(q.get(), linkIndex)
  linkIndex += 1
  time.sleep(5)

# Output

print("\nBad links: ")
printList(badLinks)
print("\nOutgoing links: ")
printDict(outgoingLinks)
print("\nGraphic Links: ")
printDict(graphicLinks)
print("\nIgnored Links: ")
printDict(disallowedLinks)
print("\nParsed links: ")
printDict(parsedLinks)
# print("\nAll links: ")
# printList(processedLinks)
print("\nDuplicate content: ")
printTupleList(duplicateContent)

printTopTwenty()

print("\n")
printMatrix()
print("\n")
