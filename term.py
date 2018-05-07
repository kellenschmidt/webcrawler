import math

class Term:

  def __init__(self, text, count):
    self.text = text
    self.count = count
    self.tfIdf = 0.0
    self.similarity = 0.0

  def __repr__(self):
    return("text: " + self.text
      + ", count: " + str(self.count)
      + ", tf-idf: " + str(self.tfIdf)
      + ", similarity: " + str(self.similarity))

  def increment(self):
    self.count += 1


  def setTfIdf(self, idf):
    tf = 1 + math.log10(self.count)
    self.tfIdf = tf * idf
    # print(self.text + ": tf-idf = " + str(self.tfIdf))

  def setSimilarity(self, totalTfIdf):
    if totalTfIdf != 0:
      self.similarity = self.tfIdf / totalTfIdf
    else:
      self.similarity = 0
    # print(self.text + ": similarity = " + str(self.similarity))
