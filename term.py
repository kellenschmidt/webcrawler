class Term:

  def __init__(self, text, count):
    self.text = text
    self.count = count
    self.tfIdf = 0
    self.normalizedTfIdf = 0

  def __repr__(self):
    return("text: " + self.text
      + ", count: " + str(self.count))

  def increment(self):
    self.count += 1


  # def add_trick(self, trick):
  #   self.tricks.append(trick)
