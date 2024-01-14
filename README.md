# RuleProcessor
This tool is based on Decoupled Rules Implementation for Effective Conceptual Model Extraction from User Stories. The tool maintains a rulebase and facilitates adding, modifying, deleting, executing, and viewing extraction rules in it. The tool makes use of extraction rulebase to extract conceptual model from user stories.

# Input
Well formed user story. 

# Output
Extraction Rulebase and Conceptual Model

# DataSets

<b>Visitor System: </b>US_VS.txt<br>
<b>Data Hub: </b>US_DH.txt<br>
<b>Planning Poker: </b>US_PP.txt<br>

# Results
<b>Results reported in the paper are summarized in the file: </b>Results.xlsx<br>
<b>Results for the Data Hub data set  are presented in the file: </b>Results_Dataset1.xlsx<br>
<b>Results for the Planning Poker data set are presented in the file: </b>Results_Dataset2.xlsx<br>

# Implementation
RuleProcessor is developed in Python. 
For NLP tasks: tokenization, POS tagging, lemmatization, and dependency parsing, we use spaCy, a free, open-source library for NLP in Python. 
We use the displacy visualizer of spaCy for visualizing type dependency graphs. 
PySwip (Python - SWI-Prolog bridge) is used to query the knowledgebase (facts + rules) written in SWI-Prolog from our Python implementation. 
We use SQLite to implement extraction rulebase and Python SQLite3 module to integrate SQLite with Python. 
PyQt5, the blend of Python and the Qt library is used for the tool's GUI. 
