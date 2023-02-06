"""Script for creating automated translations for the i18n files.

Dependencies of this script:
transformers sentencepiece sacremoses
"""

import re

import yaml
from tqdm import tqdm
from transformers import pipeline

url_pattern = (
    r"^(?:www\.)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?$"
)

languages = {
    "es": "Helsinki-NLP/opus-mt-en-es",
    "fr": "Helsinki-NLP/opus-mt-en-fr",
    "it": "Helsinki-NLP/opus-mt-en-it",
    "pt": "Helsinki-NLP/opus-mt-tc-big-en-pt",
    "zh": "Helsinki-NLP/opus-mt-en-zh",
    "ja": "Helsinki-NLP/opus-tatoeba-en-ja",
    "ru": "Helsinki-NLP/opus-mt-en-ru",
    "ar": "Helsinki-NLP/opus-mt-tc-big-en-ar",
    "hi": "Helsinki-NLP/opus-mt-en-hi",
    "id": "Helsinki-NLP/opus-mt-en-id",
}

with open("en.yml") as stream:
    try:
        file_content = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

english_content = file_content["en"]

for language, url in languages.items():
    print(f"Translating: {language}")
    translate_pipeline = pipeline(f"translation_en_to_{language}", model=url)

    final_translations = {}

    for key, value in tqdm(english_content.items()):
        print(f"Translating: {value}")
        # check if the value is only a website link with no other text, if so, don't translate
        if re.match(url_pattern, value):
            final_translations[key] = value
            continue

        try:
            translated = translate_pipeline(
                value, max_length=1024, top_k=1, top_p=1, temperature=1
            )[0]["translation_text"]
            final_translations[key] = translated
        except Exception as e:
            print(f"Error: {e}")
            # If there is an error, just use the original value
            final_translations[key] = value
            continue

    with open(f"{language}.yml", "w") as outfile:
        yaml.dump(
            {language: final_translations},
            outfile,
            default_flow_style=False,
            allow_unicode=True,
        )
