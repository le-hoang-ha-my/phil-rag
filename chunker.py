from typing import List, Dict
from transformers import AutoTokenizer
import spacy


class TextChunker:
    """
    Chunks text at sentence boundaries with overlap.
    """

    def __init__(
        self,
        tokenizer_name: str = "Qwen/Qwen3-0.6B",
        chunk_size: int = 8000,
        overlap: int = 500
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name,
            trust_remote_code=True
        )
        self.chunk_size = chunk_size
        self.overlap = overlap

        try:
            self.nlp = spacy.load("en_core_web_sm", disable=[
                                  "ner", "parser", "lemmatizer"])
            # Only enable sentencizer (much faster than full parser)
            self.nlp.enable_pipe("senter")
        except OSError:
            print("⚠️  spaCy model 'en_core_web_sm' not found.")
            print("   Installing now: python -m spacy download en_core_web_sm")
            import subprocess
            subprocess.run(
                ["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm", disable=[
                                  "ner", "parser", "lemmatizer"])
            self.nlp.enable_pipe("senter")

        print(
            f"Chunker initialized (size={chunk_size}, overlap={overlap}, spaCy)")

    def split_sentences(self, text: str) -> List[str]:
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        sentences = [s for s in sentences if s]

        return sentences

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=True))

    def chunk(self, text: str, metadata: Dict = None) -> List[Dict]:
        total_tokens = self.count_tokens(text)

        if total_tokens <= self.chunk_size:
            # No chunking needed
            return [{
                'text': text,
                'metadata': metadata or {},
                'chunk_index': 0,
                'total_chunks': 1,
                'tokens': total_tokens
            }]

        sentences = self.split_sentences(text)

        if not sentences:
            # no sentences
            return [{
                'text': text,
                'metadata': metadata or {},
                'chunk_index': 0,
                'total_chunks': 1,
                'tokens': total_tokens
            }]

        chunks = []
        current_sentences = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            # Handle very long sentences
            if sentence_tokens > self.chunk_size:
                # Save current chunk if exists
                if current_sentences:
                    chunks.append({
                        'sentences': current_sentences[:],
                        'tokens': current_tokens
                    })
                    current_sentences = []
                    current_tokens = 0

                # Add long sentence as its own chunk
                chunks.append({
                    'sentences': [sentence],
                    'tokens': sentence_tokens
                })
                continue

            # Would adding this sentence exceed limit?
            if current_tokens + sentence_tokens > self.chunk_size and current_sentences:
                # Save current chunk
                chunks.append({
                    'sentences': current_sentences[:],
                    'tokens': current_tokens
                })

                # Create overlap for next chunk
                overlap_sentences = []
                overlap_tokens = 0

                # Add sentences from end of previous chunk
                for sent in reversed(current_sentences):
                    sent_tokens = self.count_tokens(sent)
                    if overlap_tokens + sent_tokens <= self.overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_tokens += sent_tokens
                    else:
                        break

                # Start new chunk with overlap
                current_sentences = overlap_sentences
                current_tokens = overlap_tokens

            # Add sentence to current chunk
            current_sentences.append(sentence)
            current_tokens += sentence_tokens

        # Add last chunk
        if current_sentences:
            chunks.append({
                'sentences': current_sentences,
                'tokens': current_tokens
            })

        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            formatted_chunks.append({
                'text': ' '.join(chunk['sentences']),
                'metadata': metadata or {},
                'chunk_index': i,
                'total_chunks': len(chunks),
                'tokens': chunk['tokens']
            })

        return formatted_chunks


if __name__ == "__main__":
    chunker = TextChunker(chunk_size=100, overlap=20)

    # Simulate long text
    text = " ".join([f"This is sentence number {i}." for i in range(50)])

    chunks = chunker.chunk(text)

    print(f"Num tokens: {chunker.count_tokens(text)}")
    print(f"Num chunks: {len(chunks)}")
    for chunk in chunks:
        print(
            f"Chunk {chunk['chunk_index']} contains {chunk['tokens']} tokens")
