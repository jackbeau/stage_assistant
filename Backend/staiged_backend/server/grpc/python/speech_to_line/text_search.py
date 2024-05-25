import json
import logging
from thefuzz import fuzz
import string
from concurrent.futures import ThreadPoolExecutor
import sys

# Configure logging for the TextSearch class
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Use the same logger instance
logger = logging.getLogger("speech_to_line")
logger.setLevel(logging.INFO)

MAX_FAILED_ATTEMPTS = 5
SIMILARITY_THRESHOLD = 49
FORWARD_WINDOW_SIZE = 10
BACKWARD_WINDOW_SIZE = 10

class TextSearch:
    def __init__(self, chunks, mqtt_controller=None):
        self.chunks = chunks
        self.mqtt_controller = mqtt_controller
        self.current_window = self.chunks[:FORWARD_WINDOW_SIZE]  # Start with the first 10 chunks
        self.current_window_start_index = 0  # Start index of the current window
        self.failed_attempts = 0
        self.failed_transcriptions = []
        self.similarity_threshold = SIMILARITY_THRESHOLD  # Example threshold for similarity score
        self.executor = ThreadPoolExecutor(max_workers=1)  # Executor for running global search
        self.best_match = None

    def clean_text(self, text):
        # Convert text to lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def search_for_line(self, target_string):
        best_match = None
        best_score = 0

        cleaned_target_string = self.clean_text(target_string)
        target_words = cleaned_target_string.split()

        for i, chunk in enumerate(self.current_window):
            chunk_text = ' '.join(chunk['text'])
            chunk_words = chunk_text.split()

            # Crop the target string to the length of the chunk if it's longer
            if len(target_words) > len(chunk_words):
                cropped_target_string = ' '.join(target_words[:len(chunk_words)])
            else:
                cropped_target_string = cleaned_target_string

            similarity_score = fuzz.token_set_ratio(
                chunk_text,
                cropped_target_string
            )

            if similarity_score > self.similarity_threshold and  similarity_score > best_score:
                best_score = similarity_score
                best_match = {
                    'page_number': chunk.get('last_page_number'),
                    'y_coordinate': chunk.get('last_y_coordinate'),
                    'chunk_index': chunk.get('id'),
                    'chunk_text': chunk_text,
                    'input_line': cropped_target_string,
                    'similarity_score': similarity_score,
                }

        if best_match and best_score >= self.similarity_threshold:
            # Adjust the window based on the best match
            self.adjust_window(best_match['chunk_index'])
            self.failed_attempts = 0
            self.failed_transcriptions.clear()
            self.best_match = best_match
        else:
            self.failed_attempts += 1
            self.failed_transcriptions.append(cleaned_target_string)
            # if self.failed_attempts >= MAX_FAILED_ATTEMPTS:
            #     self.executor.submit(self.global_search)  # Run global search in a separate thread

        if self.mqtt_controller is not None and self.best_match is not None:
            try:
                result = self.mqtt_controller.publish(
                    "local_server/tracker/position",
                    json.dumps(self.best_match),
                    retain=True
                )
                logger.info(f"Published to MQTT topic, result: {result}")
            except Exception as e:
                logger.error(f"Failed to publish MQTT message: {e}")

        logger.info(f"Best match: '{self.best_match}' (Similarity: {best_score}%)")
        return best_match

    def adjust_window(self, best_chunk_index):
        # Move the window so that the best chunk is the second in the new window
        new_start_index = max(0, best_chunk_index - BACKWARD_WINDOW_SIZE)
        self.current_window = self.chunks[new_start_index:best_chunk_index + FORWARD_WINDOW_SIZE]
        self.current_window_start_index = new_start_index

    def global_search(self):
        logger.info("Initiating global search")
        highest_cumulative_score = 0
        best_window = None

        num_chunks = len(self.chunks)
        window_size = FORWARD_WINDOW_SIZE + BACKWARD_WINDOW_SIZE
        overlap = window_size // 2

        for i in range(0, num_chunks, overlap):  # Overlapping windows
            start_index = max(0, i - BACKWARD_WINDOW_SIZE)
            window = self.chunks[start_index:start_index + window_size]
            cumulative_score = 0

            for transcription in self.failed_transcriptions:
                for chunk in window:
                    chunk_text = " ".join(chunk['text'])
                    similarity_score = fuzz.partial_token_sort_ratio(chunk_text, transcription)
                    cumulative_score += similarity_score

            if cumulative_score > highest_cumulative_score and cumulative_score >= self.similarity_threshold * len(self.failed_transcriptions):
                highest_cumulative_score = cumulative_score
                best_window = window

        if best_window:
            self.current_window = best_window
            self.current_window_start_index = self.chunks.index(best_window[0])
            self.failed_attempts = 0
            self.failed_transcriptions.clear()
            logger.info(f"New window set based on global search with cumulative score: {highest_cumulative_score}")

# Usage example
if __name__ == "__main__":
    # This is an example. You need to ensure you have a file "server/storage/transcripts/output_extracted_data.json"
    # with the appropriate format for this to work correctly.
    chunks = [
        # Example chunks
        {"id": 0, "text": ["this", "is", "a", "test"], "last_page_number": 1, "last_y_coordinate": 100},
        {"id": 1, "text": ["another", "chunk", "of", "text"], "last_page_number": 1, "last_y_coordinate": 150},
        # Add more chunks as needed for testing
    ]
    text_search = TextSearch(chunks)
    result = text_search.search_for_line("test")
    print(result)
