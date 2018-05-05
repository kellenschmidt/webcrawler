# Kellen's Web Crawler

Please note that in an attempt to gain the best understanding of web crawlers, I attempted a very ambitious scope of building my crawler **completely from scratch, without extending any existing crawler libraries**.

As a result my on-time submission did not meet all of the requirements, but a little over an hour past the deadline, the program now meets every requirement.

I ask you to please consider my ambitions scope, and be lenient in allowing me to submitting a working project just a short time after the official deadline.

I've had a TON of fun making my web crawler and feel that writing it from scratch has truely helped me understand everything on a much deeper level.

Thank you!

## Instructions

### Setup
- Install Python 3.6.1 or later

### Usage
```
python crawler.py <depth> <stopwords_file>
```

`depth` is the number of links to evaluate (Max of ~60 in my testing)

`stopwords_file` is a text file containing the stopwords to ignore

## Tools Used
- Python
- Beautiful Soup - Python library for parsing html

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
- The program properly handles relative links
  - For links that don't start with "http://" (i.e. relative links), the program tests whether adding the domain name to the relative link makes it valid
  - If it does make it valid then it adds it to the queue for processing
  - If it doesn't then it marks it as a bad link
- A custom User-Agent for the webcrawler is sent with every HTTP request
- Correctly categorizes: Broken links, Outgoing links, Graphic links, Disallowed links, Duplicate links, and Valid(Parsable) links
