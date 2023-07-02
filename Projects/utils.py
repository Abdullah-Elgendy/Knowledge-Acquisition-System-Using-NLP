import scispacy
import os
from pyquery import PyQuery as pq
import spacy
import collections
from spacy import displacy
from spacy.matcher import Matcher 
from spacy.tokens import Span
import pandas as pd
import re
import csv
import xml.etree.ElementTree as ET
from django.core.exceptions import ValidationError
import nltk
nlp = spacy.load("en_ner_bc5cdr_md")


def validate(inp):
    pattern = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"  #only URLS
    m = re.match(pattern, str(inp))
    return (m is not None)
   
def text_extract(url):
   url_in = url
   validate(url_in)
   
   if url_in != None:
     page = pq(url=url_in)
     paragraph = page("p")
     paragraph = str(paragraph.text())
     doc = nlp(paragraph[0:3000])
     return doc
   
   else:
     return None 
 
def lists_to_df (disease,symptomsList):
    df = pd.DataFrame(columns=['Disease' , 'Symptoms'])
    df.loc[0,'Disease'] = disease[0]
    df.loc[0,'Symptoms'] = symptomsList[0:]
    df.to_csv("output.csv")

def extractDiseaseSymptom(doc):
    matcher = Matcher(nlp.vocab)
    pattern1 = [[{"LOWER":"symptoms"}, {"POS": "ADP"}, {"POS": "ADJ"} , {"POS": {"IN": ["NOUN" , "PROPN"]}}],
               [{"LOWER":"symptoms"}, {"POS": "ADP"}, {"POS": {"IN": ["NOUN" , "PROPN"]}}],
               [{"LOWER":"signs"},{"POS": "ADP"}, {"POS": {"IN": ["NOUN" , "PROPN"]}}]]

    pattern2 = [{"ENT_TYPE": "DISEASE"}]
           
    matcher.add("matching_1", pattern1)

    matches = matcher(doc)
    disease=[]
    for match_id, start, end in matches:
      span = doc[start:end]
      span_text = span.text
      span_text= re.sub(r'\W+', '', span_text)
      disease.append(span.text)
    
    if not disease:
      disease.append("Disease") 

    matcher.remove("matching_1")

    matcher.add("matching_2", [pattern2])
    matches = matcher(doc)
    
    symptoms=[]                 
    for match_id, start, end in matches:       #extract symptoms
      span = doc[start:end]
      symptom_text = str.lower(span.text)
      symptom_text = re.sub(r"\d+", "", symptom_text)
      symptom_text= re.sub(r'\W+', '', symptom_text)
      symptoms.append(symptom_text)


    symptomsList = []
    processed_texts = []
    for symptom in symptoms:  #remove duplicates
      if symptom not in symptomsList:
         symptomsList.append(symptom)     
         
    return disease, symptomsList
  
def create_xmlRules(root,inference,cluster,symptomsList):
    #Define the input and output file paths
    output_file = "output.xml"
    input_file = "output.csv"

    #Read the CSV file and extract the data
    with open(input_file, "r") as f:
      reader = csv.reader(f)
      data = list(reader)

    # Create the Rule element with the Name and game attributes
    rule = ET.SubElement(cluster, "Rule")
    rule.set("Name", "r1")
    rule.set("game", f"{data[1][1]}")  #changed the "game" value to be the first element in the CSV which will be "symptoms of ______"

    # Loop over the data and create a Tuple element for each row
    for symptom in symptomsList: 
        tuple_elem = ET.SubElement(rule, "Tuple")
        tuple_elem.set("Cpt", "member")
        tuple_elem.set("Prop", "Symptoms")
        tuple_elem.set("Val", symptom)
        
    #Write the XML tree to the output file
    with open(output_file, "w") as f:
       f.write('<?xml version="1.0" encoding="windows-1256"?>\n')
       f.write(ET.tostring(root, encoding="unicode"))

def validate_file_extension(value):
     if not value.name.endswith('.xml'):
      raise ValidationError(u'File must extension must be .XML')

def extractSymptomsFromXML(file):
  tree = ET.parse(file)
  root = tree.getroot()
  inference = root.find('Inference') #enter the "inference" tag in the xml
  cluster = inference.find('Cluster') #enter the "Cluster" tag in the xml
  list = [] #list for collecting symptom "Val"s in each rule
  
  for rules in cluster.findall('Rule'):#loop on rules
    for symptom in rules.findall('Tuple'): #loop on each tuple in the rule
     list.append(symptom.get('Val')) #append the "Val" into the list
  
  return list  

def xml_reasoning(file, userchoice):
  choiceList =  userchoice
  tree = ET.parse(file)
  root = tree.getroot()
  inference = root.find('Inference') #enter the "inference" tag in the xml
  cluster = inference.find('Cluster') #enter the "Cluster" tag in the xml
  
  count = 0
  
  rule1 = ""
  perc1 = 0
  rule2= ""
  perc2 = 0
  rule3 = ""
  perc3 = 0
  rule4 = ""
  perc4 = 0
  
  for rules in cluster.findall('Rule'):  #loop on rules
    list = []   #list for collecting symptom "Val"s in each rule
    for symptom in rules.findall('Tuple'): #loop on each tuple in the rule
     list.append(symptom.get('Val')) #append the "Val" into the list 
    count += 1
    name = rules.get('game')
    perc = int(len(set(choiceList) & set(list))/len(list) * 100)
    
    if count == 1:
      rule1 = name
      perc1 = perc
    elif count == 2:
      rule2 = name
      perc2 = perc
    elif count == 3:
      rule3 = name
      perc3 = perc
    else:
      rule4 = name
      perc4 = perc
    
  if perc1 > max(perc2 , perc3 , perc4):
    return rule1 , perc1
  
  elif perc2 > max(perc1 , perc3 , perc4):
    return rule2 , perc2
  
  elif perc3 > max(perc2 , perc1 , perc4):
    return rule3 , perc3
  
  else:
    return rule4 , perc4
    
    #if collections.Counter(choiceList) == collections.Counter(list): #once all of the rule's "Val"s are appended compare the list to the choice list of the user input
    #  return rules.get('game') #if the two lists match return the name of the rule and terminate the loop.
    #else:
    #  continue #if they don't match continue the loop and move to next rule.

def main(url_list):
   output_file = "output.xml"

   # Create the root element of the XML tree
   root = ET.Element("Root")

   # Create the Inference element with the Name attribute
   inference = ET.SubElement(root, "Inference")
   inference.set("Name", "differentiation_model")

   # Create the Cluster element with the Name attribute
   cluster = ET.SubElement(inference, "Cluster")
   cluster.set("Name", "differentiation_model")
   
   for url in url_list: 
     doc = text_extract(url)
     
     if doc != None:
       disease,symptomsList = extractDiseaseSymptom(doc)
       lists_to_df (disease,symptomsList)
       create_xmlRules(root,inference,cluster,symptomsList)