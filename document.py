import math
from term import Term

class Document:

  def __init__(self, id="", title="", text="", terms=[], url=""):
    self.id = id
    self.title = title
    self.text = text
    self.terms = []
    self.url = url
    self.totalTfIdf = 0.0
    self.totalSimilarity = 0.0

    for termText in terms:
      self.addToTerms(termText)

  def getDocumentFrequency(self, word):
    for term in self.terms:
      if term.text == word:
        return term.count

    return 0

  def addToTerms(self, newTermText):
    for index, term in enumerate(self.terms):
      if term.text == newTermText:
        self.terms[index].increment()
        return
  
    self.terms.append(Term(newTermText, 1))

  def getTermsString(self):
    returnStr = ""
    for term in self.terms:
      returnStr += "\n  " + str(term)
    
    return returnStr

  def setTotalTfIdf(self):
    sumOfSquares = 0
    for term in self.terms:
      sumOfSquares += term.tfIdf * term.tfIdf

    self.totalTfIdf = math.sqrt(sumOfSquares)
    print("Total tf-idf: " + str(self.totalTfIdf))

  def setTotalSimilarity(self, termsArray):
    sumOfProducts = 0
    for queryTerm in termsArray:
      queryTermSimilarity = 0
      for term in self.terms:
        if term.text == queryTerm.text:
          queryTermSimilarity = queryTerm.similarity
          sumOfProducts += term.similarity * queryTermSimilarity
          break

    self.totalSimilarity = sumOfProducts
    print("Total similarity: " + str(self.totalSimilarity))

  def addTitleBonus(self, queryTerms):
    for term in queryTerms:
      if self.title.lower().find(term.text) != -1:
        print("Bonus for doc #", self.id)
        self.totalSimilarity += 0.25
        return

  def __repr__(self):
    return("\nid: " + str(self.id)
      + "\ntitle: " + self.title
      + "\ntext: " + self.text
      + "\nterms: " + self.getTermsString()
      + "\nurl: " + self.url
      + "\ntotal tf-idf: " + str(self.totalTfIdf)
      + "\ntotal similarity: " + str(self.totalSimilarity))
