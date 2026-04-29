from pipeline.preprocessor import normalize
text, entities = normalize("what causes heart attack in a 45 year old?")
print(text)     # "what causes myocardial infarction in a 45 year old?"
print(entities) # ['causes', 'myocardial', 'infarction', '45', 'year', 'old']