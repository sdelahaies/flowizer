def prompt_fn(Input=None,param={}):
    return {"text":"""Extract the product\'s name and estimated carbon footprint from the document below:
<document>    
{document}
</document>
return the information as json object using the following keys:

'name': 'product_name',
'footprint': 'product_footprint'
'unit': 'footprint_unit'

where the product_name is a string (eg Dell inspiron 3546), the product_footprint is a float (eg 456), and the footprint_unit is a string eg (eg kgCO2e).
Do not add any additional information to the output.
"""}