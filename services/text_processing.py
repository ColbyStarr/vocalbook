import re

def read_and_chunk_text(file_path):
    """
    Reads a text file, removes artificial line breaks, and fixes split words.
    Returns a list of clean sentences.
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Combine lines into a single text block with paragraph breaks handled
    combined_text = []
    buffer_line = ""

    for line in lines:
        line = line.strip()

        if not line:  # Blank line, treat as paragraph break
            if buffer_line:
                combined_text.append(buffer_line)
                buffer_line = ""
            continue

        # Check for hyphenated line breaks (word split across lines)
        if line.endswith('-'):
            buffer_line += line[:-1]  # Strip hyphen, keep joining
        else:
            if buffer_line:
                buffer_line += " " + line
            else:
                buffer_line = line

    if buffer_line:
        combined_text.append(buffer_line)

    # Now `combined_text` is a list of clean paragraphs.
    full_text = "\n\n".join(combined_text)

    # Remove any weird double spaces (could happen after rejoining)
    full_text = re.sub(r'\s+', ' ', full_text).strip()

    # Sentence split
    sentences = re.split(r'(?<=[.!?]) +', full_text)

    # Final cleanup (in case any splits or artifacts created empty sentences)
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences
