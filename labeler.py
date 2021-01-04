import logging
import json
from os.path import join
import os
import sys
import subprocess

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# This dictionary contains as keys the bank names and as values the extractors

Dict_extractors = {
    "barclays": "barclays-extractor",
    "hsbc": "HSBC-extractor",
    "lloyds": "Lloyds-extractor",
    "natwest": "Natwest-extractor",
    "rbs": "RBS-extractor",
    "santander": "Santander-extractor",
    "tsb": "TSB-extractor"
}

# This dictionary contains as keys the the entities names for NER and as values the entities tags for NER

BS_NER = {
    "from_date": "FD",
    "to_date": "TD",
    "Sort-Code": "SC",
    "IBAN": "IBAN",
    "account_name": "AN",
    "account_address": "AA",
    "account_number": "ANU",
    "Bic": "BIC",
    "account_type": "AT",
    "closing_balance": "CB",
    "opening_balance": "OB",
    "issue_date": "ID",
    "payments_out": "POW",
    "payments_in": "PID",
    "payment_date": "PDA",
    "payment_details": "PDE",
    "paid_in": "PI",
    "paid_out": "PO",
    "balance": "B",
    "payment_type": "PT",
    "other_withdrawals": "OW",
    "other_deposits": "OD",
    "average_account_balance": "AAB",
    "branch_transit_number": "BTN",
    "bank_entity": "BE"
}
# This dictionary contains as keys the the entity names from the extractors and as values the entity tags for NER

SWITCHER = {
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
    "date": "PDA",
    "description": "PDE",
    "paid_out": "PO",
    "balance": "B",
    "paid_in": "PI"
}


class labeler():
    def __init__(self, bank_name, data_folder=None):
        # Fix the bank name
        self.bank_name = bank_name

        # Fix the paths to the sjons with the entities
        self.base_path = os.getcwd()
        self.data_path = join(self.base_path, data_folder) if data_folder is not None else join(self.base_path, "Data")
        self.switcher = SWITCHER

        # Fixing file names and extractor
        self.extractor = Dict_extractors[bank_name.lower()]
        self.num_files = self.extract_file_names()

    def extract_file_names(self):
        """ Extracts the names of all the files in data_path"""
        logger.info(" Creating a list of files to be labeled ...")
        # List the files to be labeled
        list_files = []
        for file in os.listdir(self.data_path):
            if ".pdf" in file:
                list_files.append(file)
        self.list_files = list_files
        return len(list_files)

    def extract_entities(self, my_output=None):
        """ Extracts the entities from each file listed and creates a list of dictionaries entity type (old one)
        and value (text)"""
        logger.info(" Extracting entities with the extractors and creating a list of dictionaries {entity:value} ...")
        # Extract entities with Dig tools
        self.dict_entities = {}

        # Loop over files
        for file in self.list_files:
            if not my_output:
                output = self.extractor(join(self.data_path, file))
            else:
                with open(my_output, 'r') as f1:
                    output = json.load(f1)
            pages = output['extractionResults']['documentTypes'][0]['documents'][0]['pages']

            # Loop over pages
            list_ = []
            for page in pages:
                list_entities = page['fields']

                # loop over the list of entities
                for entity in list_entities:
                    dict_ = {}
                    if "key" in entity.keys() and entity["key"] in self.switcher.keys() and entity["value"] is not None:
                        dict_[entity["key"]] = entity["value"]
                        list_.append(dict_)
                    elif "key" in entity.keys() and entity["key"]=="lines":
                        transactions = entity["value"]
                        for transaction in transactions:
                            for transaction_entity in transaction:
                                if transaction_entity["value"]!="":
                                    dict_[transaction_entity["key"]] = transaction_entity["value"]
                                    list_.append(dict_)
                    else:
                        pass
            self.dict_entities[file] = list_

    def extract_text(self):
        """ Extracts the entities from each file listed and creates a list of dictionaries entity type (old one)
        and value (text)"""
        logger.info(" Extracting text from pdfs ...")
        self.dict_text = {}
        # Loop over files
        for file in self.list_files:
            text = ""
            pdf = pdfplumber.open(join(self.data_path, file))
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                text += "\n" + page_text
            self.dict_text[file] = text

    def tagger(self):
        """ replace the values from the entities by their value per word plus the positional tag,
         using the switcher json file"""
        logger.info(" using the extracted entities and text to pre-tag the bank statements ...")
        # Loop over files
        for file in self.list_files:
            list_entities = self.dict_entities[file]
            doc = self.dict_text[file]
            for entity in list_entities:
                for key, value in entity.items():  # There is only one key per dictionary, not a real loop
                    tag = self.switcher.get(key, "Invalid field")
                    if tag== "Invalid field":
                        print(key)
                    value = value.strip()
                    new_value = value
                    values_list = value.split(' ')

                    if len(values_list) == 1:
                        new_value = new_value.replace(values_list[0], values_list[0] + ' [' + tag + '-U]', 1)

                    if len(values_list) == 2:
                        new_value = new_value.replace(values_list[0], values_list[0] + ' [' + tag + '-B]', 1)
                        new_value = new_value.replace(values_list[1], values_list[1] + ' [' + tag + '-L]', 1)

                    if len(values_list) > 2:
                        new_value = new_value.replace(values_list[0], values_list[0] + ' [' + tag + '-B]', 1)
                        in_values = values_list[1:-1]
                        for val in in_values:
                            new_value = new_value.replace(val, val + ' [' + tag + '-I]', 1)
                        new_value = new_value.replace(values_list[-1], values_list[-1] + ' [' + tag + '-L]', 1)
                    doc = doc.replace(value, new_value)

            tagged_file_path = join(self.data_path, file.split(".")[0] + ".txt")
            with open(tagged_file_path, "w+", encoding="utf-8") as file:
                file.write(doc)
                file.close()

    def tag_all(self, my_output=None):
        self.extract_file_names()
        self.extract_entities(my_output=my_output)
        self.extract_text()
        self.tagger()


def get_logger(
        LOG_FORMAT='%(asctime)s %(name)s %(levelname)s %(message)s',
        LOG_NAME=__name__,
        LOG_FILE_INFO='file.log',
        LOG_FILE_ERROR='file.err'):
    log = logging.getLogger(LOG_NAME)
    log_formatter = logging.Formatter(LOG_FORMAT)

    # comment this to suppress console output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    log.addHandler(stream_handler)

    file_handler_info = logging.FileHandler(LOG_FILE_INFO, mode='w')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.INFO)
    log.addHandler(file_handler_info)

    file_handler_error = logging.FileHandler(LOG_FILE_ERROR, mode='w')
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.ERROR)
    log.addHandler(file_handler_error)

    log.setLevel(logging.INFO)

    return log


if __name__ == '__main__':
    # Logger
    logger = get_logger()

    # Install the library pdfplumber and import it
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pdfplumber'])
    import pdfplumber

    # tag the documents
    output_path = join(os.getcwd(), "Data", "output.json")
    logger.info("Create the class labeler")
    My_labeler = labeler(bank_name="barclays", data_folder="Data")
    My_labeler.tag_all(my_output=output_path)
