import json
import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = os.getenv("INPUT_FILE_PATH")
OUTPUT_FILE = os.getenv("OUTPUT_FILE_PATH")


def extract_questions_and_answers(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    rows = []

    for item in data["questions"]:
        question = item["question"]
        answers = item["answers"]
        solution = item["solution"]

        correct_answer = answers[solution]

        rows.append({
            "question": question,
            "answer": correct_answer
        })

    return pd.DataFrame(rows)


def main():
    df = extract_questions_and_answers(INPUT_FILE)

    print(df.head())
    print(f"\nTotal questions: {len(df)}")

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()