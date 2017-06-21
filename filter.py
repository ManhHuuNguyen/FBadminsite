bad_word_repertoire =["dm", "dcm", "fuck", "ong chu viettel", "vcl"]


def filter(string):
    return any([bad_word in string for bad_word in bad_word_repertoire])


