import os
from pathlib import Path
from svlearn.common.utils import (
    ensure_directory,
    directory_readable,
    directory_writable,
)
from svlearn.text.text_chunker import ChunkText
import logging as log


class DirectoryChunker:
    def __init__(self, path: str, chunk_size=2000):
        ensure_directory(path)
        directory_readable(path)
        self.path = path
        self.chunker = ChunkText()
        self.chunker.similarity_threshold = -0.2
        self.chunker.chunk_size = chunk_size
        self.all_chunks = []

    def process(self, overwrite: bool = False) -> "DirectoryChunker":
        if self.all_chunks:
            log.warn("Chunks already exist.")

            if overwrite:
                log.warn("Overwriting existing chunks.")
            else:
                log.warn("Not overwriting existing chunks.")
                return

        all_chunks: list[str] = []
        dir = Path(self.path)
        dir.mkdir(parents=True, exist_ok=True)
        textfiles = list(dir.rglob("*.txt"))
        self.textfiles = textfiles

        log.info(f"Found {len(textfiles)} text files in {self.path}")

        if not textfiles:
            log.warn(f"No text files found in {self.path}")
            return

        for textfile in textfiles:
            with open(textfile, "r") as f:
                file_content = f.read()
                chunks = self.chunker.create_chunks(file_content)
                named_chunks = [(textfile.stem, chunk) for chunk in chunks]
                all_chunks.extend(named_chunks)

        log.info(f"Created {len(all_chunks)} chunks from {len(textfiles)} text files")
        self.all_chunks = all_chunks
        return self

    def save(self, path: Path) -> "DirectoryChunker":
        ensure_directory(path)
        directory_writable(path)
        part = 0
        current_name = ""
        for idx, named_chunk in enumerate(self.all_chunks):
            source_name = named_chunk[0]
            if source_name != current_name:
                current_name = source_name
                part = 0
            else:
                part += 1
            output_file = f"{path}/{source_name}_{part}.txt"
            with open(output_file, "w") as f:
                f.write(named_chunk[1])

        log.info(f"Saved {len(self.all_chunks)} chunks to {path}")
        return self


if __name__ == "__main__":
    source_dir = "/home/asif/Downloads/chunks2"
    target_dir = "/home/asif/Downloads/youtube/supportvectors-mp3/text-chunks"
    chunker = (
        DirectoryChunker(path=source_dir).process(overwrite=True).save(path=target_dir)
    )
    log.info(
        f"Created {len(chunker.all_chunks)} chunks from {len(chunker.textfiles)} text files"
    )
