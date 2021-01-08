import re
import pandas as pd

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


def cleaner(path_file):
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
    output = clean_entities(list_entities, SWITCHER)
    df["tag"] = output
    df["text"] = df["word"] + " " + df["tag"] + " "
    text = df["text"].tolist()
    text = "".join(text)
    re.sub("\s+", " ", text)
    return text


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


text = cleaner(path_file='BankStatements (3).tsv')
print(text)

