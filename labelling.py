import logging
import json
from os.path import join
import os
import pdfplumber


Dict_extractors = {
    "barclays": "barclays-extractor"
}

class labeler():
    def __init__(self, bank_name, data_path=None):
        # Fix the bank name
        self.bank_name = bank_name

        # Fix the paths to the sjons with the entities
        self.base_path = os.getcwd()
        self.data_path = data_path if data_path is not None else join(self.base_path, "Data")
        self.switcher_path = join(self.base_path, "Dictionaries", "switcher.json")

        # Load the jsons as dictionaries in python
        with open(self.switcher_path, 'r') as f1:
            self.switcher = json.load(f1)
            f1.close()
        self.BS_NER_path = join(self.base_path, "Dictionaries", "BS_NER.json")
        with open(self.BS_NER_path, 'r') as f2:
            self.BS_NER = json.load(f2)
            f2.close()

        #
        self.extractor = Dict_extractors[bank_name.lower()]
        self.num_files = self.extract_file_names()

    def extract_file_names(self):
        """ Extracts the names of all the files in data_path"""
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
        # Extract entities with Dig tools
        self.dict_entities = {}


        # Loop over files
        for file in self.list_files:
            if not my_output:
                output = self.extractor(join(data_path, file))
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

            self.dict_entities[file] = list_

    def extract_text(self):
        """ Extracts the entities from each file listed and creates a list of dictionaries entity type (old one)
        and value (text)"""
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
         using the switecher json file"""
        # Loop over files
        for file in self.list_files:
            list_entities = self.dict_entities[file]
            doc = self.dict_text[file]
            for entity in list_entities:
                for key, value in entity.items(): # There is only one key per dictionary, not a real loop
                    tag = self.switcher.get(key, "Invalid field")
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
                        new_value = new_value.replace(values_list[0], values_list[0] + ' [' + tag + '-L]', 1)
                    doc = doc.replace(value, new_value)

            tagged_file_path = join(self.base_path, file.split(".")[0] + ".txt")
            with open(tagged_file_path, "w+", encoding="utf-8") as file:
                file.write(doc)
                file.close()
                
    def tag_all(self):
        self.extract_file_names()
        self.extract_entities(my_output=None)
        self.extract_text()
        self.tagger()