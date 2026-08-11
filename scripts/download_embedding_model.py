from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-large-en-v1.5"
OUTPUT_PATH = "../model/bge-large-en-v1.5"

print("Downloading model...")

model = SentenceTransformer(MODEL_NAME)

model.save(OUTPUT_PATH)

print(f"Model saved to: {OUTPUT_PATH}")