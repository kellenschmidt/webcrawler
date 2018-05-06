# Kellen's Web Crawler

## Instructions

### Setup
- Install Python 3.6.1 or later

### Usage
```
python crawler.py
```

`depth`: automatically set to 109 (enough to crawl entire website)

`stopwords_file`: automatically set to `/stopwords.txt`

## Project 2 Responses

1. What was changed to support the second half of the project?

- To save the titles of every document I:
  - Added an array of strings to contain document titles
  - Added added logic to read the title html element if it exists or the page url if it doesn't and set that to the page title
  - ...

2. How did you determine the leaders? Do you agree with the clustering? Is 5 reasonable?

- ...

3. What happens if a user enters a word that is not in the dictionary? What happens if a user enters a stop word?

- If the user enters a query which is all stopwords then no search is executed, an error message is shown, and the user is asked to try a new query
- If the user enters a query which is mix of stopwords and valid terms then a warning is shown and the query is executed with the stopword(s) removed
- If the user enters a non-word term (ex. 123-abc) then an error message is shown and the user is asked to try a new query
- If the user enters a word that is not in the dictionary then...

4. What document/query weighting scheme did you implement?

- The cosine similarity weighting scheme that I implemented was LTC.LTC

5. Explain why you believe the results are correct

- ...

## Implementation Details

### Data structures
- `index`: Main index is a dictionary of dictionaries
  - The key is the unique document index
  - The value for each key is a dictionary of token-frequency pairs
  - Example:
  ```
  {
    0: {
      test: 4,
      computer: 7,
      apples: 1,
      oranges: 3,
    },
    1: {
      peaches: 3,
      coconuts: 9,
      lemons: 2
    }
  }
  ```

- `documentIndicies`: List of all of the unique document indexes
- `documents`: List of tuples containing the url and text content of every link that has been parsed
- `allWords`: Dictionary of every word that has been parsed, associated with its collection frequency
- `q`: Queue of urls that have been found and are candidates for crawling

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

- The program properly handles relative links when found in the documents
- A custom User-Agent for the webcrawler is sent with every HTTP request
- Correctly categorizes: Broken links, Outgoing links, Graphic links, Disallowed links, Duplicate links, and Valid(Parsable) links
