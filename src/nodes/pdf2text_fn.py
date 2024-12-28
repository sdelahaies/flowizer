import pdftotext

def pdf2text_fn(input:dict,param={}) -> dict:
    """
Extract text content from a PDF file by reading the file and converting it to text using pdftotext library.

Args:
    input (dict): A dictionary containing the file input information.
    param (dict, optional): Additional parameters for processing. Defaults to an empty dictionary.

Returns:
    dict: A dictionary with the extracted text content from the PDF file, or an error dictionary if an exception occurs.
"""
    key=list(input.keys())[0]
    filename = input[key]['filename']
    try:
        with open(f"../uploads/{filename}", "rb") as f:
            pdf = pdftotext.PDF(f)
            return {'text': "\n\n".join(pdf)}
    except Exception as e:
        return {'error': str(e)}