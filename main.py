import logging
from os.path import join
from labelling import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
logger.propagate = False


if __name__ == '__main__':
    test = labeler(bank_name="barclays")
    test.extract_file_names()
    test.extract_entities(my_output=join(test.data_path, "output.json"))
    test.extract_text()
    test.tagger()