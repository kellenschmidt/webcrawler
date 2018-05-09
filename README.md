# Kellen's Web Crawler

## Instructions

### Setup
- Install Python 3.6.1 or later

### Usage
```
python crawler.py
```

## Project 2 Responses

1. What was changed to support the second half of the project?

- To save the titles, urls, and cosine similarities of every document I:
  - Create classes for Document and Term to store all of the information about documents and terms
    - Document contains the page's ID, text, title, url, array of terms, total tf-idf, and total similarity
    - Term contains a word's, text, count, tf-idf, and similarity with respect to the document it's found in
  - Restructured the application to save and read data from an array of Document objects
  - Added added logic to read the title html element if it exists or the page url if it doesn't and set that to the page title

2. How did you determine the leaders? Do you agree with the clustering? Is 5 reasonable?

- After the documents were clustered, the leaders of each cluster were determined by the calculating the document with the minimum euclidean distance to the centroid coordinates of each cluster
- The followers for each cluster were ordered by their cosine similarity to the leader of their cluster
- My clustering results are correct because:
    - Documents which contain the same content (building1.txt and building2.txt) were clustered together and the follower's similarity score to the leader was 1.0 which was to be expected because a similarity score of 1.0 indicates a perfect match
    - Other similar files such as the "Mary" files or the "Basketball" files were clustered together
    - The documents within a cluster were similar, and documents from different clusters were dissimilar
- Setting the number of clusters to 5 was reasonable because it prevented the clusters from being too large or too small and becoming trivial. It also resulted in clusters that were had high intra-cluster similarity and low inter-cluster similarity

3. What happens if a user enters a word that is not in the dictionary? What happens if a user enters a stop word?

- If the user enters a query which is all stopwords then no search is executed, an error message is shown, and the user is asked to try a new query
- If the user enters a query which is mix of stopwords and valid terms then a warning is shown and the query is executed with the stopword(s) removed
- If the user enters a non-word term (ex. 123-abc) then an warning message is shown and the query is executed with the non-word term removed
- If the user enters a word that is not in the corpus then it has no effect on the search results

4. What document/query weighting scheme did you implement?

- The cosine similarity weighting scheme that I implemented was LTC.LTC

5. Explain why you believe the results are correct

- My query search results were correct because:
    - The only documents that were returned for each query were those which contained at least one of the query terms and they were ordered by similarity score
    - When a query was made which matched a document exactly (such as "buildingone buildingtwo buildingthree") then the simiarity score of the returned results was 1.0 for each of identically matching documents
    - Also similarity scores were accurate because I recreated the "Mary had a little lamb" example from the sample excel document and the similarity scores that the program reported matched the output of the excel document
    - When a query search term was found in the title of a document, 0.25 was added to the similarity score, which is why some results had a similarity score of slighly higher than 1.0

## Other Details

### Key properties

- Politeness:
  - The program obeys the robots.txt file
  - The program waits 5 seconds between making successive HTTP requests

- Robustness:
  - The program does not stop or break when it encounters bad links
    - Uses exception handling when links return 404 errors
  - The program rewrites relative links as absolute links

- Duplicates:
  - The program checks for both duplicate links and content and doesn't re-index duplicate content

### Special features

- Properly parses and applies the rules found in the robots.txt file
- The program properly handles relative links when found in the documents
- A custom User-Agent for the webcrawler is sent with every HTTP request
- Correctly categorizes: Broken links, Outgoing links, Graphic links, Disallowed links, Duplicate links, and Valid(Parsable) links
