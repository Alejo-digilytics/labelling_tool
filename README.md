# labelling_tool

This repository contains a labeller class which can be used to label bank statements for our NER task. 
Process: 
  0. Move to the working directory and running the following command on terminal `pip install -r requiremnts.txt` to install the necessary library
  1. load the bank statements of a concreate bank into the folder Data. Example: bank statements from Barclays
  2. Add the function to convert from a pdf into a json file already existing in Digilytics. Example:
                Dict_extractors = {
                  "barclays": "barclays-extractor"
                  }
  3. In main.py initialize the class with the bank statement type and run method tag_all. Example:
                test = labeler(bank_name="barclays")
                test.tag_all()
  4. Pick the tagged txt files from the folder Data and repeat the process from 1
  
It can be use as a sigle script to run if one adds the jsons as dictionaries in the fil labeller.py.
