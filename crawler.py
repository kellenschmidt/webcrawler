import requests, queue, sys, re, collections, time
from bs4 import BeautifulSoup
from print import *

q = queue.Queue()
parsedLinks = {}
outgoingLinks = {}
disallowedLinks = {}
badLinks = {}
graphicLinks = {}
processedLinks = []
duplicateContent = []
disallowedDirs = []
graphicExtensions = ["gif", "jpg", "jpeg", "png", "pdf", "xlsx"]
textExtensions = ["htm", "html", "txt", "php"]
startingLink = 'http://lyle.smu.edu/~fmoore/'
myUserAgent = "Kellen's Web Crawler 2.0"
headers = {
  "User-Agent": myUserAgent
}
documents = []
documentIndicies = []
index = {}
allWords = {}

# Functions

def readRobotsTxt():
  result = requests.get(startingLink + "robots.txt", headers=headers, timeout=5.0)
  plain = result.text

  lines = plain.split("\n")

  allowed = False
  for line in lines:
    if line[0] == "#":
      continue
    if(line[0:11] == "User-agent:"):
      userAgent = line[11:].strip()
      if userAgent == "*" or userAgent == myUserAgent:
        allowed = True
      else:
        allowed = False
    elif line[0:9] == "Disallow:" and allowed == True:
      disallowedDirs.append(line[9:].strip())

def getDictionaryWithAddedItem(theDictionary, newItem):
  if newItem in theDictionary:
    newCount = theDictionary.get(newItem) + 1
  else:
    newCount = 1

  theDictionary.update({newItem: newCount})
  return theDictionary

def createTokensDict(list):
  newDict = {}
  for item in list:
    newDict = getDictionaryWithAddedItem(newDict, item)

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

def processLink(url):
  if url in processedLinks:
    return

  processedLinks.append(url)

  if isDisallowedDir(url):
    global disallowedLinks
    disallowedLinks = getDictionaryWithAddedItem(disallowedLinks, url)
    return

  try:
    code = requests.get(url, headers=headers)
  except Exception:
    if isRelativeLink(url):
      url = startingLink + url
      code = requests.get(url, headers=headers)
    else:
      global badLinks
      badLinks = getDictionaryWithAddedItem(badLinks, url)
      return

  if isGraphicLink(url):
    global graphicLinks
    graphicLinks = getDictionaryWithAddedItem(graphicLinks, url)
    return

  if not re.search(r"https?://(lyle|s2).smu.edu/~fmoore", url):
    global outgoingLinks
    outgoingLinks = getDictionaryWithAddedItem(outgoingLinks, url)
    return
    
  global parsedLinks
  parsedLinks = getDictionaryWithAddedItem(parsedLinks, url)
  plain = code.text
  prettySoupStr = BeautifulSoup(plain, "html.parser").prettify()
  soup = BeautifulSoup(prettySoupStr, "html.parser")
  
  stopwordsFile = ' '.join(sys.argv[2:])
  with open(stopwordsFile) as f:
    stopwords = f.read().splitlines()

  for link in soup.find_all('a'):
    linkSrc = str(link.get('href'))
    addtoQueue(linkSrc)
  
  plainText = soup.get_text().lower()
  duplicateTuplesList = [item for item in documents if item[1] == plainText]
  for tuple in duplicateTuplesList:
    duplicateContent.append((url, tuple[0]))
  if len(duplicateTuplesList) == 0:
    documents.append((url, plainText))
    
  unfilteredTokens = plainText.split()
  withoutNonwords = removeNonwords(unfilteredTokens)
  filteredTokens = diff(withoutNonwords, stopwords)

  linkIndex = len(parsedLinks)
  index.update({linkIndex: createTokensDict(filteredTokens)})
  documentIndicies.append(linkIndex)
  for token in filteredTokens:
    global allWords
    allWords = getDictionaryWithAddedItem(allWords, token)

def getDocumentFreq(token):
  freq = 0
  for docIndex in documentIndicies:
    if index.get(docIndex).get(token):
      freq = freq + 1
  return freq

def printMatrix():
  print("Term-Document Frequency Matrix:")
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
  print("\nTop 20 Tokens:")
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

print("\nLoading...\n\n")

readRobotsTxt()

maxNumLinks = int(sys.argv[1])
addtoQueue(startingLink)
linkIndex = 0
while(not q.empty() and linkIndex < maxNumLinks):
  processLink(q.get())
  linkIndex += 1
  # time.sleep(5)

# Output

print("\nBad links: ")
printDict(badLinks)
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

print("Parsing status: ")
if q.empty():
  print("Parsed entire website, not limited by user-defined number of pages to retrieve\n")
else:
  print("Did not parse entire website, limited by user-defined number of pages to retrieve, consider increasing the input, number of pages remaining: " + str(q.qsize()) + "\n")
  while(not q.empty()):
    print(q.get())
