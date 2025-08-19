import pdfplumber

content = ""
with pdfplumber.open("ollama/test/daryl_resume.pdf") as pdf:
    first_page = pdf.pages[0]
    content = first_page.extract_text()
    # print(content)

# Character Chunking
char_chunks = []

def chunk_text_by_chars(text, chunk_size=500):
    return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size-100)]

for i, chunk in enumerate(chunk_text_by_chars(content)):
    char_chunks.append({
        "text": chunk,
        "page": 1,  # since you used first_page
        "chunk_index": i,
        "source": "daryl_resume.pdf"
    })

# # Line Chunking
# line_chunks = []

# def chunk_text_by_lines(text, num_lines=1):
#     lines = text.split('\n')
#     return [lines[i:i+num_lines] for i in range(0, len(lines), num_lines)]

# Add Metadata to each chunk
for i, chunk in enumerate(chunk_text_by_chars(content)):
    char_chunks.append({
        "text": chunk,
        "page": 1,  # since you used first_page
        "chunk_index": i,
        "source": "daryl_resume.pdf"
    })

print(char_chunks)