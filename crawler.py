import requests, queue, sys, re, collections, time, math, numpy
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from print import *
from document import Document

q = queue.Queue()
graphicExtensions = ["gif", "jpg", "jpeg", "png", "pdf", "xlsx"]
textExtensions = ["htm", "html", "txt", "php"]
startingLink = 'http://lyle.smu.edu/~fmoore/'
myUserAgent = "Kellen's Web Crawler 2.0"
headers = {
  "User-Agent": myUserAgent
}
documents = []
allWords = {}
stopwords = []
links = {}
disallowedDirs = []

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

def addtoQueue(newLink):
  if links.get(newLink):
    return

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

  if links.get(url):
    return

  if isDisallowedDir(url):
    links.update({url: "disallowed"})
    return

  if isOutgoingLink(url):
    links.update({url: "outgoing"})
    return

  response = requests.get(url, headers=headers, timeout=5.0)
  statusCode = response.status_code

  if statusCode != 200:
    links.update({url: "bad"})
    return

  if isGraphicLink(url):
    links.update({url: "graphic"})
    return

  links.update({url: "parsed"})
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
  for document in documents:
    if document.text == plainText:
      links.update({url: "duplicate"})
      return

  unfilteredTokens = plainText.split()
  withoutNonwords = removeNonwords(unfilteredTokens)
  filteredTokens = diff(withoutNonwords, stopwords)

  linkIndex = len(documents)
  if(ogSoup.title):
    docTitle = ogSoup.title.string
  else:
    docTitle = url

  for token in filteredTokens:
    global allWords
    allWords = getDictionaryWithAddedItem(allWords, token)

  documents.append(Document(linkIndex, docTitle, plainText, filteredTokens, url))

def getDocumentFreq(word):
  freq = 0
  for document in documents:
    for term in document.terms:
        if term.text == word:
          freq = freq + 1
          break

  return freq

def getDocumentByWord(word):
  for document in documents:
    if document.text == word:
      return document
  
  return Document()

def printMatrix():
  print("Term-Document Frequency Matrix:")
  print("Word\t\t\t\t\t\t", end="")
  for document in documents:
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
    for document in documents:
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

def printLinks(type):
  for key, value in links.items():
    if value == type:
      print(key)

def isInvalidTerm(term):
  if term[len(term)-1].isalnum() and term[0].isalpha():
    return False
  else:
    return True

def getDocumentById(id):
  for document in documents:
    if document.id == id:
      return document
  
  return Document()

def getTextSummaryString(textStr):
  textAsTokens = textStr.split()
  showElipsis = "..." if len(textAsTokens) > 20 else ""
  return ' '.join(textAsTokens[:20]) + showElipsis

def printDocInfo(document):
  print("Title: ", document.title)
  print("Text: ", getTextSummaryString(document.text))
  print("URL: ", document.url)

def handleQuery(queryStr):
  queryTerms = queryStr.split()
  stopwordsInQuery = []
  for term in queryTerms:
    if isInvalidTerm(term):
      print("Warning: Invalid query, " + term + " is not a valid query term")
      queryTerms.remove(term)
    elif term in stopwords:
      stopwordsInQuery.append(term)
  
  if len(queryTerms) == 0:
    print("Error: Invalid query, no valid query terms")
    return
  elif len(stopwordsInQuery) == len(queryTerms):
    print("Error: Invalid query, all terms are stopwords")
    return
  elif len(stopwordsInQuery) > 0:
    print("Warning: The following terms were ignored because they are stopwords:")
    printList(stopwordsInQuery)
    print()
    queryTerms = diff(queryTerms, stopwordsInQuery)

  # Calculate IDFs
  idfs = {}
  numDocuments = float(len(documents))
  # print("numDocuments: " + str(numDocuments))
  for word in allWords:
    # print("DocFreq: " + str(getDocumentFreq(word)))
    idf = math.log10(numDocuments / getDocumentFreq(word))
    idfs.update({word: idf})

  # print("IDF's:")
  # printDict(idfs)

  # Calculate tf-idfs
  for document in documents:
    # print("Doc #" + str(document.id))
    for term in document.terms:
      term.setTfIdf(idfs.get(term.text))

  # Create query as document
  queryDocument = Document(-1, "Query", queryStr, queryTerms, "query")
  for term in queryDocument.terms:
    # print("Query term")
    idfForQueryTerm = idfs.get(term.text)
    if idfForQueryTerm:
      term.setTfIdf(idfForQueryTerm)
    else:
      term.setTfIdf(0)

  for document in documents:
    # print("Doc #" + str(document.id))
    document.setTotalTfIdf()

  # print("Query Doc")
  queryDocument.setTotalTfIdf()
  
  for document in documents:
    # print("Doc #" + str(document.id))
    for term in document.terms:
      term.setSimilarity(document.totalTfIdf)

  for term in queryDocument.terms:
    # print("Query term")
    term.setSimilarity(queryDocument.totalTfIdf)

  for document in documents:
    # print("Doc #" + str(document.id))
    document.setTotalSimilarity(queryDocument.terms)
    document.addTitleBonus(queryDocument.terms)
    # print(document)

  printTopDocuments()

def getEuclideanDistance(vector1, vector2):
  return numpy.linalg.norm(vector1-vector2)

def handleCluster():
  corpus = []
  for document in documents:
    corpus.append(document.filteredText)  

  vectorizer = TfidfVectorizer()
  tfidfMatrix = vectorizer.fit_transform(corpus)
  kmeans = KMeans(n_clusters=5).fit(tfidfMatrix)
  labels = kmeans.labels_

  for clusterIndex in range(0, 5):
    doc_ids_in_cluster = []

    for labelIndex, label in enumerate(labels):
      if clusterIndex == label:
        doc_ids_in_cluster.append(labelIndex)

    tfidfsForCluster = tfidfMatrix[doc_ids_in_cluster]

    print("Cluster #", clusterIndex+1 , sep="")
    # print(tfidfsForCluster)

    distancesFromCenter = []
    for tfidfColumn in tfidfsForCluster:
      distancesFromCenter.append(getEuclideanDistance(kmeans.cluster_centers_[0], tfidfColumn))

    minVal, minIndex = min((val, idx) for(idx, val) in enumerate(distancesFromCenter))
    
    print("  Leader:\n-----------")
    leaderDoc = getDocumentById(doc_ids_in_cluster[minIndex])
    printDocInfo(leaderDoc)
    print("  Followers:\n--------------")
    for index, doc_id in enumerate(doc_ids_in_cluster):
      if index != minIndex:
        followerDoc = getDocumentById(doc_id)
        print("Id:", doc_id)
        printDocInfo(followerDoc)
        
    print()





def printTopDocuments():
  documentResults = {}
  for document in documents:
    documentResults.update({document.id: document.totalSimilarity})

  d = collections.Counter(documentResults)

  if d.most_common(1)[0][1] == 0:
    print("\nSorry your query returned no results :(\n")
  else:
    print("Top Results:\n")

  for k, v in d.most_common(6):
    if v == 0:
      return
    document = getDocumentById(k)
    printDocInfo(document)
    print("Score: ", document.totalSimilarity)
    print()

# Main

print("\n\nLoading...\n\n")

readRobotsTxt()

addtoQueue(startingLink)
# addtoQueue("http://s2.smu.edu/~fmoore/textfiles/mary1.txt")
# addtoQueue("http://s2.smu.edu/~fmoore/textfiles/mary2.txt")
# addtoQueue("http://s2.smu.edu/~fmoore/textfiles/mary3.txt")
# addtoQueue("http://s2.smu.edu/~fmoore/textfiles/mary4.txt")

linkIndex = 0
while(not q.empty() and linkIndex < 100):
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
  print("\"Cluster\" - View the clustering of the documents")
  print("\nEnter your query: " , end='')
  userQuery = input()
  userQuery = userQuery.lower()
  print("\n------------------------------------------------------------------------\n")

  if userQuery == "stop":
    print("Goodbye!\n\n")
    break
  elif userQuery == "stats":
    print("Bad links:")
    printLinks("bad")
    print("\nOutgoing links:")
    printLinks("outgoing")
    print("\nGraphic Links:")
    printLinks("graphic")
    print("\nIgnored Links:")
    printLinks("disallowed")
    print("\nParsed links:")
    printLinks("parsed")
    print("\nDuplicate content: ")
    printLinks("duplicate")
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
    print(documents)
  elif userQuery == "c":
    handleCluster()
  else:
    handleQuery(userQuery)
