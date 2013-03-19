class License(object):
    def __init__(self, short_name, long_name, url, text):
        self.short_name = short_name
        self.long_name = long_name
        self.url = url
        self.text = text

licenses = {
    "CC BY-NC 3.0" : License("CC BY-NC 3.0",
                         "Creative Commons Attribution-NonCommercial"
                         "3.0 Unported",
                         "http://creativecommons.org/licenses/by-nc/3.0/",
                         "This dataset is licensed as {short_name} (see "
                         "{url}). You are free to copy, distribute, transmit,"
                         " and adapt the data for non-commercial purposes, "
                         "provided that you give reference to the "
                         "publication specified in the metadata of this data "
                         "file."
                         ),
    "CC BY-NC-SA 3.0" : License("CC BY-NC-SA 3.0",
                         "Creative Commons "
                         "Attribution-NonCommercial-ShareAlike 3.0 Unported",
                         "http://creativecommons.org/licenses/by-nc-sa/3.0/",
                         "This dataset is licensed as {short_name} (see "
                         "{url}). You are free to copy, distribute, transmit, "
                         "and adapt the data for non-commercial purposes, "
                         "provided that you give reference to the publication "
                         "specified in the metadata of this data file. If you "
                         "alter, transform, or build upon this work, you may "
                         "distribute the resulting work only under the same "
                         "or similar license to this one."
                         ),
    }
