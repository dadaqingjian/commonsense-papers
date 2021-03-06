import re
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import spacy
nlp = spacy.load("en", disabled=["ner", "parser"])

"""
Plan to include statistics of
    - authors
    - keywords: non-stopping words in title
"""
paper_cnt = 0
author_cnt = Counter()
kwds_cnt = Counter()
venue_cnt = defaultdict(int)
my_stopwords = {"commonsense", "knowledge", "natural", "language"}
with open("README.md", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if re.search(r"^\*\*([^\*]+)\*\*", line):   # title
            title = re.search(r"^\*\*([^\*]+)\*\*", line).group(1)
            keywords = {x.lemma_.lower() for x in nlp(title) if not (x.is_stop or x.is_punct or x.lemma_.lower() in my_stopwords)}
            kwds_cnt.update(keywords)
            paper_cnt += 1
            try:
                beg = line.rfind(r"** ") + 3
                end = line.find("[") - 1
                venue_text = line[beg:end]
                if ")" in venue_text:
                    venue_text = venue_text[venue_text.find(")")+1:]
                venue = venue_text.strip().split()[0]
                venue_cnt[venue] += 1
            except Exception as e:
                pass
            continue
        if re.search(r"^\*.+\*$", line):   # author
            authors = [x.strip() for x in line[1:-1].split(", ")]
            author_cnt.update(authors)

kwds_cnt = pd.DataFrame(pd.Series(kwds_cnt).sort_values(ascending=False), columns=["count"])
author_cnt = pd.DataFrame(pd.Series(author_cnt).sort_values(ascending=False), columns=["count"])
venue_cnt = pd.DataFrame(pd.Series(venue_cnt).sort_values(ascending=False), columns=["count"])

# print("HTML")
# print("\n--Keyword--\n")
# print(kwds_cnt.head(10).to_html())
# print("\n--Author--\n")
# print(author_cnt.head(10).to_html())
# print("\n--Venue--\n")
# print(venue_cnt.head(5).to_html())

readme = open("README.md", encoding="utf-8").read()
readme = re.sub(r'<anchor id="cnt">(.*?)</anchor>', f'<anchor id="cnt">{paper_cnt}</anchor>', readme)
html0 = kwds_cnt.head(10).to_html()
readme = re.sub(r'<anchor id="keyword">\n(.*?)\n</anchor>', f'<anchor id="keyword">\n{html0}\n</anchor>', readme, flags=re.DOTALL)
html0 = author_cnt.head(10).to_html()
readme = re.sub(r'<anchor id="researcher">\n(.*?)\n</anchor>', f'<anchor id="researcher">\n{html0}\n</anchor>', readme, flags=re.DOTALL)
html0 = venue_cnt.head(5).to_html()
readme = re.sub(r'<anchor id="venue">\n(.*?)\n</anchor>', f'<anchor id="venue">\n{html0}\n</anchor>', readme, flags=re.DOTALL)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("Results (for human read)")
print("\n--Keyword--\n")
print(kwds_cnt.head(10))
print("\n--Author--\n")
print(author_cnt.head(10))
print("\n--Venue--\n")
print(venue_cnt.head(5))
print(f"Paper count: {paper_cnt}")