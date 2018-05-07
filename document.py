from term import Term

class Document:

  def __init__(self, id, title, text, terms, url):
    self.id = id
    self.title = title
    self.text = text
    self.terms = []
    self.url = url

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

  def __repr__(self):
    return("\nid: " + str(self.id)
      + "\ntitle: " + self.title
      + "\ntext: " + self.text
      + "\nterms: " + self.getTermsString()
      + "\nurl: " + self.url)
