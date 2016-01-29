# Han the Converter

Based on the file structure created by [_Luke the Downloader_](../Luke_the_Downloader/EconstorDownloader.ipynb), _Han the Coverter_ extracts the plaintext from the PDF files in the `data/pdf` subdirectory and writes that text into the `plaintext` attribute of the corresponding JSON file. Moreover, does it [_guess_](https://pypi.python.org/pypi/langdetect/1.0.1) the language of the document and adds this information as well under the `lang` attribute.

## Time, multiprocessing and ressources

Plaintext extraction is a computationally-intensive task (20-30 seconds for a 10-pages document is a realistic estimate). Therefore, multiprocessing is used in this script, as it allows extracting text from multiple documents simultaneously. Your machine should also have ~500MB of RAM per CPU core (e.g. ~4GB for an [Intel Core i7 4770K](http://ark.intel.com/de/products/75123/Intel-Core-i7-4770K-Processor-8M-Cache-up-to-3_90-GHz))

## Checkpoint and progress

You can easily interrupt the processing whenever you want. The script writes a checkpoint file every 30 seconds that allows it to resume calulations. Therefore, restarting the script will do the trick.

## Data quality, format and filtering

The data is Unicode-encoded using UTF-8. Extracting plaintext from PDF files is not a straighforward process. Encoding problems, password-protected files, a large variety of text formatting are only a few of the potential problems. To mitigate some of these problems a filter module (`processingPdfFiles/filter.py`) is used to correct some of the common errors. You should adapt this module to your own needs. Nevertheless, _some_ noise in the data is inevitable.
