import re
from pathlib import Path

from PyPDF2 import PdfReader


def read_and_chunk_text(file_path, batch_size=10) -> dict[int, list[str]]:
    """
    Reads a text file, removes artificial line breaks, and fixes split words.
    Returns a list of clean sentences.
    """

    file_path = Path(file_path)
    if file_path.suffix.lower() == ".pdf":

        reader = PdfReader(str(file_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        lines = text.splitlines()
    else:
        with open(file_path, "r", encoding="utf-8") as file:
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
        if line.endswith("-"):
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
    full_text = re.sub(r"\s+", " ", full_text).strip()

    ELLIPSIS_PLACEHOLDER = "<<<ELLIPSIS>>>"
    # This matches 3+ periods separated by spaces, like ". . ." or ". . . . ."
    full_text = re.sub(r"(?:\.\s){2,}\.", ELLIPSIS_PLACEHOLDER, full_text)

    # Sentence split
    sentences = re.split(r"(?<=[.!?]) +", full_text)

    sentences = [s.replace(ELLIPSIS_PLACEHOLDER, "...") for s in sentences]

    processed_sentences = []

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        while len(s) > 250:
            # Try to find a space near the midpoint
            midpoint = len(s) // 2
            split_index = s.rfind(" ", 0, midpoint)

            if split_index == -1:
                split_index = s.find(" ", midpoint)  # fallback to forward search
            if split_index == -1:
                # No spaces? Hard split (edge case)
                split_index = 250

            first_part = s[:split_index].strip()
            s = s[split_index:].strip()

            processed_sentences.append(first_part)
        if s:
            processed_sentences.append(s)

    sentences = processed_sentences

    chunks = {}
    for i in range(0, len(sentences), batch_size):
        group_index = i // batch_size
        chunks[group_index] = sentences[i : i + batch_size]

    return chunks


def count_text_chunks(file_path, batch_size=10):
    file_path = Path(file_path)
    if file_path.suffix.lower() == ".pdf":

        reader = PdfReader(str(file_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        lines = text.splitlines()
    else:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

    combined_text = []
    buffer_line = ""

    for line in lines:
        line = line.strip()

        if not line:
            if buffer_line:
                combined_text.append(buffer_line)
                buffer_line = ""
            continue

        if line.endswith("-"):
            buffer_line += line[:-1]
        else:
            if buffer_line:
                buffer_line += " " + line
            else:
                buffer_line = line

    if buffer_line:
        combined_text.append(buffer_line)

    full_text = "\n\n".join(combined_text)
    full_text = re.sub(r"\s+", " ", full_text).strip()

    ELLIPSIS_PLACEHOLDER = "<<<ELLIPSIS>>>"
    # This matches 3+ periods separated by spaces, like ". . ." or ". . . . ."
    full_text = re.sub(r"(?:\.\s){2,}\.", ELLIPSIS_PLACEHOLDER, full_text)

    sentences = re.split(r"(?<=[.!?]) +", full_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    sentences = [s.replace(ELLIPSIS_PLACEHOLDER, "...") for s in sentences]

    total_chunks = (len(sentences) + batch_size - 1) // batch_size
    return total_chunks
