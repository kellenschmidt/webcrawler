import requests, queue, sys, re, collections, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from print import *
from document import Document
from term import Term

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
documentTitles = []
allWords = {}
stopwords = []
documentObjects = []

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
  if url[0:4] != "http":
    return True
  else:
    return False

def isGraphicLink(url):
  lastDot = url.rfind('.')
  suffix = url[lastDot+1:]

  if suffix in graphicExtensions:
    return True
  else:
    return False

def isOutgoingLink(url):
  if not re.search(r"https?://(lyle|s2).smu.edu/~fmoore", url):
    return True
  else:
    return False

def isDisallowedDir(url):
  for dir in disallowedDirs:
    if re.search(dir, url) or re.search(dir, urljoin(startingLink, url)):
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
  if isRelativeLink(url):
    url = urljoin(startingLink, url)

  if url in processedLinks:
    return
  else:
    processedLinks.append(url)

  if isDisallowedDir(url):
    global disallowedLinks
    disallowedLinks = getDictionaryWithAddedItem(disallowedLinks, url)
    return

  if isOutgoingLink(url):
    global outgoingLinks
    outgoingLinks = getDictionaryWithAddedItem(outgoingLinks, url)
    return

  try:
    response = requests.get(url, headers=headers, timeout=5.0)
    statusCode = response.status_code
  except Exception:
    global badLinks
    badLinks = getDictionaryWithAddedItem(badLinks, url)
    return

  if statusCode != 200:
    badLinks = getDictionaryWithAddedItem(badLinks, url)
    return

  if isGraphicLink(url):
    global graphicLinks
    graphicLinks = getDictionaryWithAddedItem(graphicLinks, url)
    return

  global parsedLinks
  parsedLinks = getDictionaryWithAddedItem(parsedLinks, url)
  plain = response.text

  ogSoup = BeautifulSoup(plain, "html.parser")
  ogSoupBody = ogSoup
  if ogSoup.body:
    ogSoupBody = ogSoup.body
  if ogSoupBody.script:
    [s.extract() for s in ogSoupBody('script')]
  prettySoupStr = ogSoupBody.prettify()
  soup = BeautifulSoup(prettySoupStr, "html.parser")
  
  stopwordsFile = "stopwords.txt"
  with open(stopwordsFile) as f:
    global stopwords
    stopwords = f.read().splitlines()

  for aTag in soup.find_all('a'):
    linkSrc = str(aTag.get('href'))
    addtoQueue(urljoin(url, linkSrc))
  for imgTag in soup.find_all('img'):
    linkSrc = str(imgTag.get('src'))
    addtoQueue(urljoin(url, linkSrc))

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
  documentIndicies.append(linkIndex)
  docTitle = ""
  if(ogSoup.title):
    docTitle = ogSoup.title.string
  else:
    docTitle = url

  for token in filteredTokens:
    global allWords
    allWords = getDictionaryWithAddedItem(allWords, token)

  newDocumentObject = Document(linkIndex, docTitle, plainText, filteredTokens, url)
  documentObjects.append(newDocumentObject)

def getDocumentFreq(word):
  freq = 0
  for document in documentObjects:
    for term in document.terms:
        if term.text == word:
          freq = freq + 1
          break

  return freq

def printMatrix():
  print("Term-Document Frequency Matrix:")
  print("Word\t\t\t\t\t\t", end="")
  for document in documentObjects:
    print("Doc #", document.id, sep="", end="\t")
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
      print("", end="\t")
    for document in documentObjects:
      termFound = False
      for term in document.terms:
        if term.text == word:
          print(term.count, end='\t')
          termFound = True
      if not termFound:
        print("0", end='\t')
  print()

def printTopTwenty():
  print("Top 20 Tokens:")
  print("Token\t\tCollectionFreq\tDocumentFreq")
  d = collections.Counter(allWords)
  for k, v in d.most_common(20):
    print(k, end="\t")
    if len(k) < 8:
      print("\t", end="")
    print(v, getDocumentFreq(k), sep="\t\t")

def isInvalidTerm(term):
  if term[len(term)-1].isalnum() and term[0].isalpha():
    return False
  else:
    return True

def handleQuery(queryStr):
  queryTerms = queryStr.split()
  stopwordsInQuery = []
  for term in queryTerms:
    if isInvalidTerm(term):
      print("Error: Invalid query, " + term + " is not a valid query term")
      return
    elif term in stopwords:
      stopwordsInQuery.append(term)
  
  if len(stopwordsInQuery) == len(queryTerms):
    print("Error: Invalid query, all terms are stopwords")
    return
  elif len(stopwordsInQuery) > 0:
    print("Warning: The following terms were ignored because they are stopwords:")
    printList(stopwordsInQuery)
    queryTerms = diff(queryTerms, stopwordsInQuery)

  # Calculate all cosine similarities
  print("\n\nEvaluating query...\n")
  printList(queryTerms)



# Main

print("\n\nLoading...\n\n")

readRobotsTxt()

addtoQueue(startingLink)
linkIndex = 0
while(not q.empty() and linkIndex < 109):
  processLink(q.get())
  linkIndex += 1
  # time.sleep(5)

print("Finished loading!!!\n\n\n")

print("******************************************************")
print("*       Kellen's Web Crawler and Search Engine       *")
print("******************************************************")

userQuery = ""
while(userQuery != "stop"):
  print("\n------------------------------------------------------------------------\n")
  print("Optional commands (case insensitive):")
  print("\"Stop\" - Exit the program")
  print("\"Stats\" - List information about the links")
  print("\"Top 20\" - View the top 20 most common words")
  print("\"Matrix\" - Display the term-document frequency matrix")
  print("\"Status\" - Determine whether the whole site has been parsed or not")
  print("\nEnter your query: " , end='')
  userQuery = input()
  userQuery = userQuery.lower()
  print("\n------------------------------------------------------------------------\n")

  if userQuery == "stop":
    print("Goodbye!\n")
    break
  elif userQuery == "stats":
    print("Bad links:")
    printDict(badLinks)
    print("\nOutgoing links:")
    printDict(outgoingLinks)
    print("\nGraphic Links:")
    printDict(graphicLinks)
    print("\nIgnored Links:")
    printDict(disallowedLinks)
    print("\nParsed links:")
    printDict(parsedLinks)
    print("\nTitles:")
    printList(documentTitles)
    # print("\nAll links: ")
    # printList(processedLinks)
    print("\nDuplicate content: ")
    printTupleList(duplicateContent)
  elif userQuery == "top 20":
    printTopTwenty()
  elif userQuery == "matrix":
    printMatrix()
  elif userQuery == "status":
    print("Parsing status: ")
    if q.empty():
      print("Parsed entire website, not limited by user-defined number of pages to retrieve, number of links evaluated: " + str(linkIndex))
    else:
      print("Did not parse entire website, limited by user-defined number of pages to retrieve, consider increasing the input, number of pages remaining: " + str(q.qsize()))
      while(not q.empty()):
        print(q.get())
  elif userQuery == "obj":
    print(documentObjects)
  else:
    handleQuery(userQuery)
    print("\nSorry, no results :(")
