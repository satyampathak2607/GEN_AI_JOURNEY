import pandas as pd
import os
import logging
import torch
from nlpaug.augmenter.word import BackTranslationAug

def run_pipeline():
    # === Set up paths ===
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "Data", "Raw_X", "sentences.csv")
    save_path = os.path.join(base_dir, "..", "Data", "Processed_X", "augmented_sentences.csv")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # === Logging ===
    logging.basicConfig(filename='augmentation.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting data augmentation pipeline.")

    # === Load data ===
    df = pd.read_csv(data_path)
    print(f"✅ Loaded data: {len(df)} rows")

    # === Use lightweight MarianMT instead of Facebook WMT19 ===
    aug = BackTranslationAug(
        from_model_name='Helsinki-NLP/opus-mt-en-de',
        to_model_name='Helsinki-NLP/opus-mt-de-en',
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    print("🔁 BackTranslationAug initialized.")
    print(f"Using device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

    # === Augment each sentence safely ===
    augmented_sentences = []
    for i, sentence in enumerate(df['text']):
        try:
            result = aug.augment(sentence)
            augmented = result[0] if isinstance(result, list) else result
            print(f"[{i+1}/{len(df)}] ✅")
        except Exception as e:
            augmented = ""
            print(f"[{i+1}/{len(df)}] ❌ Error: {e}")
        augmented_sentences.append(augmented)

    df['augmented_sentence'] = augmented_sentences
    df.to_csv(save_path, index=False)

    print(f"\n✅ Saved to {save_path}")
    logging.info(f"Saved to {save_path}")
    logging.info("Pipeline complete.")

# 🧠 Safe entry point for multiprocessing (must-have for Windows)
if __name__ == "__main__":
    run_pipeline()
