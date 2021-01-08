import re
import pandas as pd
import os
import nltk

SWITCHER = {
    "O": "O",
    "from_date": "FD",
    "to_date": "TD",
    "sort_code": "SC",
    "iban": "IBAN",
    "account_number": "ANU",
    "account_address": "AA",
    "account_name": "AN",
    "bic": "BIC",
    "account_type": "AT",
    "opening_balance": "OB",
    "closing_balance": "CB",
    "issue_date": "ID",
    "payments_out": "POW",
    "payments_in": "PID",
    "payment_date": "PDA",
    "payment_details": "PDE",
    "paid_out": "PO",
    "balance": "B",
    "paid_in": "PI",
    "payment_type": "PT"
}


def cleaner(path_file, output_path):
    df = pd.read_csv(path_file, names=["word", "tag"], sep='\t')
    list_given_entities = df["tag"].unique().tolist()

    # Check missing tags
    for key in SWITCHER.keys():
        if key in list_given_entities:
            print("We can switch", key)
        else:
            print("We can NOT switch", key)
    print("---------------------")
    for key in list_given_entities:
        if key in SWITCHER.keys():
            print("Useful", key)
        else:
            print("NOT useful", key)

    # clean tags
    list_entities = df["tag"].tolist()
    tagged_text = clean_entities(list_entities, SWITCHER)

    # Add tagged words
    df["tag"] = tagged_text
    df["text"] = df["word"] + " " + df["tag"] + " "

    # Join and clean text
    text = "".join(df["text"].tolist())
    re.sub("\s+", " ", text)

    # Split text based on real sentences
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    list_sentences = [sentence for sentence in tokenizer.tokenize(text)]

    # Split based on size
    list_ = []
    sentence_size = 18
    max_size = 35
    for line in list_sentences:
        words = line.split(" ")
        num_words = len(words)
        # Too long
        if num_words > 35:
            divider = num_words//sentence_size
            for i in range(divider):
                list_.append(" ".join(words[i*sentence_size:(i+1)*sentence_size]))
            list_.append(" ".join(words[divider*sentence_size:]))
        else:
            list_.append(line)
    for element in list_:
        if isinstance(element,list):
            print("It is  a trap")
    file = open(output_path, "w+", encoding="UTF-8")
    file.close()
    for line in list_:
        with open(output_path, "a", encoding="UTF-8") as the_file:
            the_file.write(line + "\n")

def clean_entities(list_entities, SWITCHER):
    last_entity = ""
    last_bilou = ""
    position = 0
    output = []
    for entity in list_entities:
        # select only relevant entities
        if entity not in SWITCHER:
            pass
        else:
            # do O case first
            if entity == "O":
                label = ""
                bilou = ""
            else:
                if last != entity:
                    if list_entities[position + 1] == entity:
                        bilou = "-B"
                    else:
                        bilou = "-U"
                elif last_bilou == "-B" or last_bilou == "-I":
                    if position + 1 < len(list_entities) and list_entities[position + 1] == entity:
                        bilou = "-I"
                    elif position + 1 < len(list_entities) and list_entities[position + 1] != entity:
                        bilou = "-L"
                    elif position + 1 == len(list_entities):
                        bilou = "-L"
                label = "[" + SWITCHER[entity] + bilou + "]"
        output.append(label)
        last_bilou = bilou
        last = entity
        position += 1
    return output

path_file='BankStatements.tsv'
FILE_PATH = os.path.join(os.getcwd(), "Data", path_file.split(".tsv")[0] + ".txt")
cleaner(path_file=path_file, output_path=FILE_PATH)