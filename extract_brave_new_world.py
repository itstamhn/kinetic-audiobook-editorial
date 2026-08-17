import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

book_path = '/Users/tamhn/Downloads/Brave New World (Aldous Huxley) (z-library.sk, 1lib.sk, z-lib.sk).epub'
book = epub.read_epub(book_path)

items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
c01_item = items[5] # OEBPS/9780795311253_epub_c01_r1.htm

soup = BeautifulSoup(c01_item.get_content(), 'html.parser')

# Clean paragraphs
paragraphs = []
for p in soup.find_all(['p', 'h1', 'h2', 'h3']):
    t = p.get_text().strip()
    # Normalize whitespaces
    t = re.sub(r'\s+', ' ', t)
    if t and t != "1":
        paragraphs.append(t)

full_chapter1_text = "\n\n".join(paragraphs)

with open("book_chapters_md/brave_new_world_ch1.txt", "w") as f:
    f.write(full_chapter1_text)

words_count = len(full_chapter1_text.split())
print(f"Extracted Chapter 1: {len(paragraphs)} paragraphs, {words_count} words.")
print("\nFirst 3 paragraphs:")
for p in paragraphs[:3]:
    print("---", p)
