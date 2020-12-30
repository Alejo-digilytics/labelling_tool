## Labeler

This repository contains a labeler class which can be used to label bank statements for our NER task. 
This version is self contained in a script. The file labeler must be added to the localization of 
the bank statements and run. 

####Process: 
  1. load the bank statements of a concrete bank into the folder Data or any other folder.
  Example:
  
            bank statements from Barclays in Data
  2. Add the extractor function, or conection to the API to convert from a pdf into a json file already 
  existing in Digilytics.
  Example:
  
                Dict_extractors = {
                  "barclays": "barclays-extractor"
                  }
  3. In the call to the class labeler initialize with the bank statement type (var: bank_name), the folder containing 
  the bank statements if it's not Data (var: data_folder) and run method tag_all.
  Example:
  
                test = labeler(bank_name="barclays", data_folder="<folder_name>")
                test.tag_all()
  4. Pick the tagged txt files from the folder Data and repeat the process from 1
