import sys
import sqlite3

import owlready2
from pyswip import Prolog
# from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QLineEdit, QVBoxLayout, QMainWindow, QGridLayout, QPlainTextEdit, QTableWidget
from PyQt5.QtWidgets import *

from PyQt5.QtGui import QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QRect,Qt

import spacy
from spacy import displacy
from spacy.symbols import pobj, ADP, VERB, xcomp, ccomp, dobj, prep, relcl, PUNCT, NOUN, PROPN, nsubj, nsubjpass, poss, ADJ, amod
from pathlib import Path

from owlready2 import *

def doReset():
    print("Reset")

    global isFactsbaseGenerated
    isFactsbaseGenerated = False
    global isTypeDepGraphGenerated
    isTypeDepGraphGenerated = False

    populateRuleTable()
    txtUserStory.setText("")
    txtUserStory.setPlaceholderText("User Story: As a <user>, I want to <function> so that <benefit>")
    txtUserStory.setReadOnly(False)
    txtareaConceptualModel.clear()
    txtareaConceptualModel.setReadOnly(True)

def doExit():
    window.close()

def showFactsBase():
    txtUserStory.setReadOnly(True)
    global isFactsbaseGenerated
    if windowRule is not None:
        windowRule.close()

    if isFactsbaseGenerated == False:
        generateFacts("knowledgebases\kbUserStory.pl")
        isFactsbaseGenerated = True

    windowRule.setWindowTitle("Show Factsbase")
    layoutFactsbaseShow = QVBoxLayout()
    lblFactsbaseShow = QLabel("Factsbase")
    txtareaFactsbaseShow = QPlainTextEdit()

    with open('knowledgebases\kbUserStory.pl', 'r') as f:
        factsbase = f.read()
        txtareaFactsbaseShow.insertPlainText(factsbase)

    # txtareaFactsbaseShow.setEnabled(False)
    btnFactsbaseShowClose = QPushButton("Close")
    btnFactsbaseShowClose.clicked.connect(closeWindowRule)
    layoutFactsbaseShow.addWidget(lblFactsbaseShow)
    layoutFactsbaseShow.addWidget(txtareaFactsbaseShow)
    layoutFactsbaseShow.addWidget(btnFactsbaseShowClose)
    containerFactsbaseShow = QWidget()
    containerFactsbaseShow.setLayout(layoutFactsbaseShow)

    windowRule.setCentralWidget(containerFactsbaseShow)

    windowRule.show()

def showTypeDepGraph():
    txtUserStory.setReadOnly(True)
    global isTypeDepGraphGenerated
    if windowRule is not None:
        windowRule.close()
    print(isTypeDepGraphGenerated)
    if isTypeDepGraphGenerated == False:
        print(isTypeDepGraphGenerated)
        print(": Inside Type Dependency Graph Generation !!")
        inputUserStory = txtUserStory.text()
        nlp = spacy.load("en_core_web_lg")
        doc = nlp(inputUserStory)
        svg = displacy.render(doc, style="dep")
        output_path = Path('knowledgebases\depUserStory.svg')
        output_path.open("w", encoding="utf-8").write(svg)
        isTypeDepGraphGenerated = True

    windowRule.setWindowTitle("Type Dependency Graph")
    layoutTypeDepShow = QVBoxLayout()
    lblTypeDepShow = QLabel("Type Dependency Graph")

    typeDepView = QWebEngineView()
    with open('knowledgebases\depUserStory.svg', 'r') as f:
        html = f.read()
        typeDepView.setHtml(html)

    btnTypeDepShowClose = QPushButton("Close")
    btnTypeDepShowClose.clicked.connect(closeWindowRule)
    layoutTypeDepShow.addWidget(lblTypeDepShow)
    layoutTypeDepShow.addWidget(typeDepView)
    layoutTypeDepShow.addWidget(btnTypeDepShowClose)
    containerTypeDepShow = QWidget()
    containerTypeDepShow.setLayout(layoutTypeDepShow)

    windowRule.setCentralWidget(containerTypeDepShow)

    windowRule.show()

def populateRuleTable():
    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    c.execute("SELECT ruleid,elementtype,consequent,antecedent FROM extraction_rules")

    tblRules.clear()
    tblRules.setRowCount(1)
    tblRules.setColumnCount(4)
    columns = ['Rule Id', 'Element Type','Rule Consequent', 'Rule Antecedent', ]
    tblRules.setHorizontalHeaderLabels(columns)

    tblRules.setColumnWidth(0, 100)
    tblRules.setColumnWidth(1, 150)
    tblRules.setColumnWidth(2, 200)
    tblRules.setColumnWidth(3, 700)

    tblRules.removeRow(0)
    rowNum = 0
    # processing data row by row
    for record in c.fetchall():
        tblRules.insertRow(rowNum)
        tblRules.setItem(rowNum, 0, QTableWidgetItem(str(record[0])))
        tblRules.setItem(rowNum, 1, QTableWidgetItem(record[1]))
        tblRules.setItem(rowNum, 2, QTableWidgetItem(record[2]))
        tblRules.setItem(rowNum, 3, QTableWidgetItem(record[3]))
        # print(record[0],record[1],record[2])
        rowNum=rowNum+1

    c.close()
    conn.close()

def closeWindowRule():
    windowRule.close()

def addRuleToDB(ruleid,elementtype,consequent,antecedent):
    print(ruleid,elementtype,consequent,antecedent)
    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    params = [(ruleid,elementtype,consequent,antecedent)]
    c.executemany("INSERT INTO extraction_rules (ruleid,elementtype,consequent,antecedent) VALUES (?,?,?,?)",params)
    conn.commit()
    populateRuleTable()
    c.close()
    conn.close()

def updateRuleInDB(ruleid,elementtype,consequent,antecedent):
    print(ruleid,consequent,antecedent)
    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    params = [(elementtype, consequent,antecedent,ruleid)]
    c.executemany("UPDATE extraction_rules SET elementtype = ? ,consequent = ? ,antecedent= ? where ruleid = ?",params)
    conn.commit()
    populateRuleTable()
    c.close()
    conn.close()

def showRule():
    if windowRule is not None:
        windowRule.close()

    windowRule.setWindowTitle("Show Rule")
    layoutRuleShow = QVBoxLayout()
    lblRuleShow = QLabel("Rule")
    txtareaRuleShow = QPlainTextEdit()
    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    ruleid = tblRules.item(tblRules.currentRow(), 0).text()
    c.execute("select consequent,antecedent from extraction_rules where ruleid = " + ruleid)
    record = c.fetchone()
    rule=record[0]+":-"+record[1]+"."
    txtareaRuleShow.insertPlainText(rule)

    c.close()
    conn.close()
    # txtareaRuleShow.insertPlainText(tblRules.currentItem().text())
    txtareaRuleShow.setEnabled(False)
    btnRuleShowClose = QPushButton("Close")
    btnRuleShowClose.clicked.connect(closeWindowRule)
    layoutRuleShow.addWidget(lblRuleShow)
    layoutRuleShow.addWidget(txtareaRuleShow)
    layoutRuleShow.addWidget(btnRuleShowClose)
    containerRuleShow = QWidget()
    containerRuleShow.setLayout(layoutRuleShow)

    windowRule.setCentralWidget(containerRuleShow)

    windowRule.show()

def executeRule():
    if windowRule is not None:
        windowRule.close()

    windowRule.setWindowTitle("Execute Rule")
    layoutRuleExecute = QVBoxLayout()
    lblRuleExecute = QLabel("Execution Results")
    txtareaRuleExecute = QPlainTextEdit()

    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    ruleid = tblRules.item(tblRules.currentRow(), 0).text()
    c.execute("select consequent,antecedent from extraction_rules where ruleid = " + ruleid)
    record = c.fetchone()

    queryToExecute = record[0]

    # with open("knowledgebases\kbUserStory.pl", "r+") as f:
    #     content = f.read()
    #     f.truncate(content.index("% Rules"))

    generateFacts("knowledgebases\kbUserStory.pl")
    with open("knowledgebases\kbUserStory.pl", "a") as f:
        f.write("% Rules" + "\n" + record[0] + ":-" + record[1] + "." + "\n")

    c.close()
    conn.close()


    txtareaRuleExecute.insertPlainText(executeQuery(queryToExecute,"knowledgebases/kbUserStory.pl"))
    # txtareaRuleExecute.setEnabled(False)
    btnRuleExecuteClose = QPushButton("Close")
    btnRuleExecuteClose.clicked.connect(closeWindowRule)
    layoutRuleExecute.addWidget(lblRuleExecute)
    layoutRuleExecute.addWidget(txtareaRuleExecute)
    layoutRuleExecute.addWidget(btnRuleExecuteClose)
    containerRuleExecute = QWidget()
    containerRuleExecute.setLayout(layoutRuleExecute)

    windowRule.setCentralWidget(containerRuleExecute)
    windowRule.show()

def addRule():
    if windowRule is not None:
        windowRule.close()
    windowRule.setWindowTitle("Add Rule")
    layoutRuleAdd = QVBoxLayout()
    lblRuleAdd = QLabel("Rule Details")
    txtRuleId = QLineEdit()
    txtRuleId.setPlaceholderText("Rule Id")
    txtRuleId.setEnabled(False)

    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    c.execute("select max(ruleid) from extraction_rules")
    ruleid = str((c.fetchone()[0])+1)
    txtRuleId.setText(ruleid)
    c.close()
    conn.close()

    comboxElementType = QComboBox()
    comboxElementType.addItems(["Class","Object Property","Data Property","Sub Class Of"])
    txtRuleConsequent = QLineEdit()
    txtRuleConsequent.setPlaceholderText("Consequent")
    txtareaRuleAntecedent = QPlainTextEdit()
    txtareaRuleAntecedent.setPlaceholderText("Antecedent")
    btnRuleAddition = QPushButton("Add Rule")
    #print("Plaintext",txtareaRuleAntecedent.toPlainText())
    btnRuleAddition.clicked.connect(lambda: addRuleToDB(txtRuleId.text(),comboxElementType.currentText(),txtRuleConsequent.text(),txtareaRuleAntecedent.toPlainText()))
    btnRuleAddClose = QPushButton("Close")
    btnRuleAddClose.clicked.connect(closeWindowRule)
    layoutRuleAdd.addWidget(lblRuleAdd)
    layoutRuleAdd.addWidget(txtRuleId)
    layoutRuleAdd.addWidget(comboxElementType)
    layoutRuleAdd.addWidget(txtRuleConsequent)
    layoutRuleAdd.addWidget(txtareaRuleAntecedent)
    layoutRuleAdd.addWidget(btnRuleAddition)
    layoutRuleAdd.addWidget(btnRuleAddClose)
    containerRuleAdd = QWidget()
    containerRuleAdd.setLayout(layoutRuleAdd)

    windowRule.setCentralWidget(containerRuleAdd)
    windowRule.show()

def updateRule():
    if windowRule is not None:
        windowRule.close()
    windowRule.setWindowTitle("Update Rule")
    layoutRuleUpdate = QVBoxLayout()
    lblRuleUpdate = QLabel("Rule Details")
    txtRuleId = QLineEdit()
    txtRuleId.setPlaceholderText("Rule Id")
    txtRuleId.setEnabled(False)

    comboxElementType = QComboBox()
    comboxElementType.addItems(["Class", "Object Property", "Data Property", "Sub Class Of"])
    txtRuleConsequent = QLineEdit()
    txtRuleConsequent.setPlaceholderText("Consequent")
    txtareaRuleAntecedent = QPlainTextEdit()
    txtareaRuleAntecedent.setPlaceholderText("Antecedent")
    btnRuleUpdation = QPushButton("Update Rule")

    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    ruleid = tblRules.item(tblRules.currentRow(), 0).text()
    c.execute("select elementtype,consequent,antecedent from extraction_rules where ruleid = " + ruleid)
    record = c.fetchone()
    txtRuleId.setText(ruleid)
    comboxElementType.setCurrentText(record[0])
    txtRuleConsequent.setText(record[1])
    txtareaRuleAntecedent.setPlainText(record[2])


    c.close()
    conn.close()

    btnRuleUpdation.clicked.connect(lambda: updateRuleInDB(txtRuleId.text(),comboxElementType.currentText(),txtRuleConsequent.text(),txtareaRuleAntecedent.toPlainText()))
    btnRuleUpdateClose = QPushButton("Close")
    btnRuleUpdateClose.clicked.connect(closeWindowRule)
    layoutRuleUpdate.addWidget(lblRuleUpdate)
    layoutRuleUpdate.addWidget(txtRuleId)
    layoutRuleUpdate.addWidget(comboxElementType)
    layoutRuleUpdate.addWidget(txtRuleConsequent)
    layoutRuleUpdate.addWidget(txtareaRuleAntecedent)
    layoutRuleUpdate.addWidget(btnRuleUpdation)
    layoutRuleUpdate.addWidget(btnRuleUpdateClose)
    containerRuleUpdate = QWidget()
    containerRuleUpdate.setLayout(layoutRuleUpdate)

    windowRule.setCentralWidget(containerRuleUpdate)
    windowRule.show()

def deleteRule():
    ruleid = tblRules.item(tblRules.currentRow(),0).text()
    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    c.execute("delete from extraction_rules where ruleid = "+ruleid)
    conn.commit()
    populateRuleTable()
    c.close()
    conn.close()
    print(ruleid)

def executeQuery(queryToExecute,knowledgeBase):

    KB = knowledgeBase
    prolog = Prolog()
    prolog.consult(KB)
    contentToDisplay = ""
    contentToDisplay = "\n"+queryToExecute+"\n"
    for soln in prolog.query("setof(t,"+queryToExecute+", _)."):
    # for soln in prolog.query(queryToExecute):
        keys = list(soln.keys())
        print(keys)
        for key in keys:
            if(not(soln[key]=="")):
                contentToDisplay = contentToDisplay + key+": "+soln[key]+"\n"
    return contentToDisplay

def ruleExecute(row,column):
    print(row)
    print(column)

    executeQuery(tblRules.item(row, column).text())

rules=[]

def extractConceptualModel():

    if isFactsbaseGenerated == False:
        generateFacts("knowledgebases\kbUserStory.pl")

    with open('knowledgebases\kbUserStory.pl', 'r') as fileToRead:
        factsbase = fileToRead.read()
    with open('knowledgebases\kbUserStoryFull.pl', 'w') as fileToWrite:
        fileToWrite.write(factsbase)

    classQueries = []
    dataPropertyQueries = []
    objectPropertyQueries = []
    subClassOfQueries = []

    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    c.execute("SELECT ruleid,elementtype,consequent,antecedent FROM extraction_rules")
    with open("knowledgebases\kbUserStoryFull.pl", "a") as f:
        f.write("% Rules" + "\n")
        for record in c.fetchall():
            ruleid = record[0]
            elementtype = record[1]
            consequent = record[2]
            antecedent = record[3]

            f.write(consequent + ":-" + antecedent + "." + "\n")

            if elementtype == "Class":
                classQueries.append(consequent)
            if elementtype == "Object Property":
                objectPropertyQueries.append(consequent)
            if elementtype == "Data Property":
                dataPropertyQueries.append(consequent)
            if elementtype == "Sub Class Of":
                subClassOfQueries.append(consequent)

    c.close()
    conn.close()

    txtareaConceptualModel.setPlainText("")

    KB = "knowledgebases/kbUserStoryFull.pl"
    prolog = Prolog()
    prolog.consult(KB)

    classes = set()
    objectPropertyRelationships = set()
    dataPropertyRelationships = set()
    subClassOfRelationships = set()
    binaryRelationships = set()

    for classQuery in classQueries:
        print("\n" + classQuery)
        print("---------- ")
        for soln in prolog.query(classQuery):
            keys = list(soln.keys())
            if len(keys) == 1:
                cls = soln[keys[0]]
                if not (cls == ""):
                    print("\n" + keys[0]+": "+cls)
                    classes.add(cls)
                    # txtareaConceptualModel.insertPlainText(cls)
                    # txtareaConceptualModel.insertPlainText("\n")
            else:
                print("Check the no. of parameters in your prolog query. It must be only one !")

    for objectPropertyQuery in objectPropertyQueries:
        print("\n" + objectPropertyQuery)
        print("------------------- ")

        for soln in prolog.query(objectPropertyQuery):
            keys = list(soln.keys())
            if len(keys) == 3:
                objectProperty = soln[keys[0]]
                domain = soln[keys[1]]
                range = soln[keys[2]]
                if not (objectProperty == "" or domain == "" or range == ""):
                    print("\n" + keys[0]+": "+objectProperty)
                    print("\n" + keys[1] + ": " + domain)
                    print("\n" + keys[2] + ": " + range)
                    objectPropertyRelationships.add(domain + " " + objectProperty + " " + range)
                    # txtareaConceptualModel.insertPlainText(domain + " " + objectProperty + " " + range)
                    # txtareaConceptualModel.insertPlainText("\n")
            else:
                print("Check the no. of parameters in your prolog query. It must be only three !")

    for dataPropertyQuery in dataPropertyQueries:
        print("\n" + dataPropertyQuery)
        print("------------------- ")

        for soln in prolog.query(dataPropertyQuery):
            keys = list(soln.keys())
            if len(keys) == 3:
                dataProperty = soln[keys[0]]
                domain = soln[keys[1]]
                range = soln[keys[2]]
                if not (dataProperty == "" or domain == "" or range == ""):
                    print("\n" + keys[0]+": "+dataProperty)
                    print("\n" + keys[1] + ": " + domain)
                    print("\n" + keys[2] + ": " + range)
                    dataPropertyRelationships.add(dataProperty + " (" + domain + "): " + range)
                    # txtareaConceptualModel.insertPlainText(dataProperty + " (" + domain + "): " + range)
                    # txtareaConceptualModel.insertPlainText("\n")
            else:
                print("Check the no. of parameters in your prolog query. It must be only three !")


    for subClassOfQuery in subClassOfQueries:
        print("\n" + subClassOfQuery)
        print("------------------- ")

        for soln in prolog.query("setof(t,"+subClassOfQuery+", _)."):
            keys = list(soln.keys())
            if len(keys) == 2:
                subClass = soln[keys[0]]
                superClass = soln[keys[1]]
                if not (superClass == "" or subClass == ""):
                    print("\n" + keys[0]+": "+subClass)
                    print("\n" + keys[1] + ": " + superClass)
                    subClassOfRelationships.add(subClass + " (" + superClass + ")")
                    binaryRelationships.add(subClassOfQuery+": "+subClass + " (" + superClass + ")")
                    # txtareaConceptualModel.insertPlainText(subClass + " (" + superClass + ")")
                    # txtareaConceptualModel.insertPlainText("\n")
            else:
                print("Check the no. of parameters in your prolog query. It must be only two !")

    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("Classes")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    for cls in classes:
        txtareaConceptualModel.insertPlainText(cls)
        txtareaConceptualModel.insertPlainText("\n")

    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("Object Properties")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    for objectPropertyRelatioship in objectPropertyRelationships:
        txtareaConceptualModel.insertPlainText(objectPropertyRelatioship)
        txtareaConceptualModel.insertPlainText("\n")

    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("Data Properties")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    for dataPropertyRelatioship in dataPropertyRelationships:
        txtareaConceptualModel.insertPlainText(dataPropertyRelatioship)
        txtareaConceptualModel.insertPlainText("\n")

    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("Inheritance Relationships")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")

    for subClassOfRelationship in subClassOfRelationships:
        txtareaConceptualModel.insertPlainText(subClassOfRelationship)
        txtareaConceptualModel.insertPlainText("\n")

def generateFacts(pKbFile):
    inputUserStory = txtUserStory.text()
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(inputUserStory)

    kb_output_path = Path(pKbFile)
    kbFile = kb_output_path.open("w", encoding="utf-8")
    # facts = set()
    facts = []
    factsRel = []
    facts.append("% Facts")
    tokenLemma = ""

    for token in doc:
        if token.pos != PUNCT:
            tokenLemma = token.lemma_.lower()
            if tokenLemma == "'s":
                tokenLemma = "aposs"

            facts.append(token.pos_.lower() + "(" + tokenLemma + ").")
            factsRel.append(token.dep_.lower() + "(" + token.head.lemma_.lower() + "," + tokenLemma + ").")

    facts.append("noun('').")
    facts.append("pron('').")
    facts.append("adp('').")
    facts.append("adj('').")
    facts.append("verb('').")
    facts.append("propn('').")
    facts.append("part('').")
    facts.append("adv('').")
    facts.append("part('').")

    factsRel.append("compound('','').")
    factsRel.append("xcomp('','').")
    factsRel.append("pobj('','').")
    factsRel.append("dobj('','').")
    factsRel.append("prep('','').")
    factsRel.append("ccomp('','').")
    factsRel.append("nsubj('','').")
    factsRel.append("nsubjpass('','').")
    factsRel.append("poss('','').")
    factsRel.append("case('','').")
    factsRel.append("amod('','').")
    factsRel.append("conj('','').")
    factsRel.append("advcl('','').")
    factsRel.append("advmod('','').")
    factsRel.append("acl('','').")
    factsRel.append("attr('','').")
    factsRel.append("aux('','').")
    factsRel.append("relcl('','').")
    factsRel.append("csubj('','').")
    factsRel.append("pcomp('','').")
    factsRel.append("dative('','').")
    factsRel.append("agent('','').")

    facts.sort(reverse=False)
    factsRel.sort(reverse=False)
    kbContent = ""

    for fact in facts:
        kbFile.write(fact + "\n")
        kbContent = kbContent+fact+"\n"

    for factRel in factsRel:
        kbFile.write(factRel + "\n")
        kbContent = kbContent+factRel+"\n"

    txtareaKnowledgeBase.insertPlainText(kbContent)
    kbFile.close()

classes = set()
objectPropertyRelationships = set()
dataPropertyRelationships = set()
subClassOfRelationships = set()

def createOntology(ontoFileName):
    print("........... CREATING Ontology.............")
    onto = get_ontology("file://D:/Amol/docs/Projects/Python/RuleProcessor/Ontology/"+ontoFileName+".owl")

    print("No. of subclass relationships: " + str(len(subClassOfRelationships)))
    print("No. of classes: " + str(len(classes)))
    print("No. of object properties: " + str(len(objectPropertyRelationships)))
    print("No. of data properties: " + str(len(dataPropertyRelationships)))

    with onto:
        for subClassOf in subClassOfRelationships:
            subClassOfParts = subClassOf.split(" ")
            superClass = subClassOfParts[1].split("(")[1].split(")")[0]
            subClass = subClassOfParts[0]
            NewSuperClass = types.new_class(superClass, (owlready2.Thing,))
            NewSubClass = types.new_class(subClass, (NewSuperClass,))
            print(superClass + " " + subClass)

        for cls in classes:
            NewClass = types.new_class(cls, (owlready2.Thing,))

        for objProp in objectPropertyRelationships:
            objPropParts = objProp.split(" ")
            objPropName = objPropParts[1]
            objPropDomain = objPropParts[0]
            objPropRange = objPropParts[2]

            propClass = types.new_class(objPropName, (owlready2.ObjectProperty,))
            propClass.domain = [onto[objPropDomain]]
            propClass.range = [onto[objPropRange]]

            print(objPropName + " " + objPropDomain + " " + objPropRange)
        # print("attendance (student): String".split(" "))
        for dataProp in dataPropertyRelationships:
            dataPropParts = dataProp.split(" ")
            dataPropDomain = dataPropParts[1].split("(")[1].split(")")[0]
            dataPropName = dataPropParts[0]
            dataPropRange = dataPropParts[2]

            propClass = types.new_class(dataPropName, (owlready2.DataProperty,))
            propClass.domain = [onto[dataPropDomain]]
            propClass.range = [str]
            print(dataPropName + " " + dataPropDomain + " " + dataPropRange)

    onto.save()
    print("........... Ontology Created Successfully.............")

def extractConceptualModelFromDataSet(dataset):
    print(dataset)
    count = 1
    for userStory in dataset.splitlines():
        kbFileName = "knowledgebases/_CME_from_Dataset/kbUserStory"+str(count)+".pl"
        extractConceptualModelFromUserStory(userStory,kbFileName)
        print("----> User Story "+str(count)+" processed. <----")
        count = count + 1

    # createOntology("CME")

    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("Classes")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    for cls in classes:
        txtareaConceptualModel.insertPlainText(cls)
        txtareaConceptualModel.insertPlainText("\n")

    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("Object Properties")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    for objectPropertyRelatioship in objectPropertyRelationships:
        txtareaConceptualModel.insertPlainText(objectPropertyRelatioship)
        txtareaConceptualModel.insertPlainText("\n")

    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("Data Properties")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    for dataPropertyRelatioship in dataPropertyRelationships:
        txtareaConceptualModel.insertPlainText(dataPropertyRelatioship)
        txtareaConceptualModel.insertPlainText("\n")

    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("Inheritance Relationships")
    txtareaConceptualModel.insertPlainText("\n")
    txtareaConceptualModel.insertPlainText("-------------------")
    txtareaConceptualModel.insertPlainText("\n")

    for subClassOfRelationship in subClassOfRelationships:
        txtareaConceptualModel.insertPlainText(subClassOfRelationship)
        txtareaConceptualModel.insertPlainText("\n")

# *******************************************************************

def extractConceptualModelFromUserStory(inputUserStory,pKbFile):
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(inputUserStory)

    kb_output_path = Path(pKbFile)
    kbFile = kb_output_path.open("w", encoding="utf-8")
    # facts = set()
    facts = []
    factsRel = []
    facts.append("% Facts")
    tokenLemma = ""

    for token in doc:
        if token.pos != PUNCT:
            tokenLemma = token.lemma_.lower()
            if tokenLemma == "'s":
                tokenLemma = "aposs"

            facts.append(token.pos_.lower() + "(" + tokenLemma + ").")
            factsRel.append(token.dep_.lower() + "(" + token.head.lemma_.lower() + "," + tokenLemma + ").")

    facts.append("noun('').")
    facts.append("pron('').")
    facts.append("adp('').")
    facts.append("adj('').")
    facts.append("verb('').")
    facts.append("propn('').")
    facts.append("part('').")
    facts.append("adv('').")
    facts.append("part('').")

    factsRel.append("compound('','').")
    factsRel.append("xcomp('','').")
    factsRel.append("pobj('','').")
    factsRel.append("dobj('','').")
    factsRel.append("prep('','').")
    factsRel.append("ccomp('','').")
    factsRel.append("nsubj('','').")
    factsRel.append("nsubjpass('','').")
    factsRel.append("poss('','').")
    factsRel.append("case('','').")
    factsRel.append("amod('','').")
    factsRel.append("conj('','').")
    factsRel.append("advcl('','').")
    factsRel.append("advmod('','').")
    factsRel.append("acl('','').")
    factsRel.append("attr('','').")
    factsRel.append("aux('','').")
    factsRel.append("relcl('','').")
    factsRel.append("csubj('','').")
    factsRel.append("pcomp('','').")
    factsRel.append("dative('','').")
    factsRel.append("agent('','').")

    facts.sort(reverse=False)
    factsRel.sort(reverse=False)
    kbContent = ""

    for fact in facts:
        kbFile.write(fact + "\n")
        kbContent = kbContent+fact+"\n"

    for factRel in factsRel:
        kbFile.write(factRel + "\n")
        kbContent = kbContent+factRel+"\n"

    txtareaKnowledgeBase.insertPlainText(kbContent)

    classQueries = []
    dataPropertyQueries = []
    objectPropertyQueries = []
    subClassOfQueries = []

    conn = sqlite3.connect('cme.db')
    c = conn.cursor()
    c.execute("SELECT ruleid,elementtype,consequent,antecedent FROM extraction_rules")
    kbFile.write("% Rules" + "\n")
    for record in c.fetchall():
        ruleid = record[0]
        elementtype = record[1]
        consequent = record[2]
        antecedent = record[3]

        kbFile.write(consequent + ":-" + antecedent + "." + "\n")
        if elementtype == "Class":
            classQueries.append(consequent)
        if elementtype == "Object Property":
            objectPropertyQueries.append(consequent)
        if elementtype == "Data Property":
            dataPropertyQueries.append(consequent)
        if elementtype == "Sub Class Of":
            subClassOfQueries.append(consequent)

    c.close()
    conn.close()
    kbFile.close()
    txtareaConceptualModel.setPlainText("")

    KB = pKbFile
    print(KB)
    prolog = Prolog()
    prolog.consult(KB)

    for classQuery in classQueries:
        print("\n" + classQuery)
        print("---------- ")
        for soln in prolog.query(classQuery):
            keys = list(soln.keys())
            if len(keys) == 1:
                cls = soln[keys[0]]
                if not (cls == ""):
                    print("\n" + keys[0]+": "+cls)
                    classes.add(cls)
                    # txtareaConceptualModel.insertPlainText(cls)
                    # txtareaConceptualModel.insertPlainText("\n")
            else:
                print("Check the no. of parameters in your prolog query. It must be only one !")

    for objectPropertyQuery in objectPropertyQueries:
        print("\n" + objectPropertyQuery)
        print("------------------- ")

        for soln in prolog.query(objectPropertyQuery):
            keys = list(soln.keys())
            if len(keys) == 3:
                objectProperty = soln[keys[0]]
                domain = soln[keys[1]]
                range = soln[keys[2]]
                if not (objectProperty == "" or domain == "" or range == ""):
                    print("\n" + keys[0]+": "+objectProperty)
                    print("\n" + keys[1] + ": " + domain)
                    print("\n" + keys[2] + ": " + range)
                    objectPropertyRelationships.add(domain + " " + objectProperty + " " + range)
                    # txtareaConceptualModel.insertPlainText(domain + " " + objectProperty + " " + range)
                    # txtareaConceptualModel.insertPlainText("\n")
            else:
                print("Check the no. of parameters in your prolog query. It must be only three !")

    for dataPropertyQuery in dataPropertyQueries:
        print("\n" + dataPropertyQuery)
        print("------------------- ")

        for soln in prolog.query(dataPropertyQuery):
            keys = list(soln.keys())
            if len(keys) == 3:
                dataProperty = soln[keys[0]]
                domain = soln[keys[1]]
                range = soln[keys[2]]
                if not (dataProperty == "" or domain == "" or range == ""):
                    print("\n" + keys[0]+": "+dataProperty)
                    print("\n" + keys[1] + ": " + domain)
                    print("\n" + keys[2] + ": " + range)
                    dataPropertyRelationships.add(dataProperty + " (" + domain + "): " + range)
                    # txtareaConceptualModel.insertPlainText(dataProperty + " (" + domain + "): " + range)
                    # txtareaConceptualModel.insertPlainText("\n")
            else:
                print("Check the no. of parameters in your prolog query. It must be only three !")


    for subClassOfQuery in subClassOfQueries:
        print("\n" + subClassOfQuery)
        print("------------------- ")

        for soln in prolog.query("setof(t,"+subClassOfQuery+", _)."):
            keys = list(soln.keys())
            if len(keys) == 2:
                subClass = soln[keys[0]]
                superClass = soln[keys[1]]
                if not (superClass == "" or subClass == ""):
                    print("\n" + keys[0]+": "+subClass)
                    print("\n" + keys[1] + ": " + superClass)
                    subClassOfRelationships.add(subClass + " (" + superClass + ")")
                    # txtareaConceptualModel.insertPlainText(subClass + " (" + superClass + ")")
                    # txtareaConceptualModel.insertPlainText("\n")
            else:
                print("Check the no. of parameters in your prolog query. It must be only two !")



#**********************************************************************************
def showDataSet(dataset, datasetSize):
    if windowRule is not None:
        windowRule.close()

    windowRule.setWindowTitle("DataSet")
    windowRule.setMinimumSize(500, 500)

    layoutDatasetShow = QVBoxLayout()
    lblDatasetShow = QLabel("Number of User Stories in the dataset")
    lblDatasetShow.setText(lblDatasetShow.text()+": "+str(datasetSize)+" --> "+str(len(dataset.splitlines())))
    txtareaDatasetShow = QPlainTextEdit()

    txtareaDatasetShow.insertPlainText(dataset)
    # txtareaDatasetShow.setEnabled(False)

    btnDatasetExtractCM = QPushButton("Extract Conceptual Model")
    btnDatasetShowClose = QPushButton("Close")
    btnDatasetShowClose.clicked.connect(closeWindowRule)
    btnDatasetExtractCM.clicked.connect(lambda: extractConceptualModelFromDataSet(txtareaDatasetShow.toPlainText()))

    layoutDatasetShow.addWidget(lblDatasetShow)
    layoutDatasetShow.addWidget(txtareaDatasetShow)

    hBoxLayoutProcessDataSetButtons = QHBoxLayout()
    hBoxLayoutProcessDataSetButtons.addWidget(btnDatasetExtractCM)
    hBoxLayoutProcessDataSetButtons.addWidget(btnDatasetShowClose)
    layoutDatasetShow.addLayout(hBoxLayoutProcessDataSetButtons)

    containerDatasetShow = QWidget()
    containerDatasetShow.setLayout(layoutDatasetShow)

    windowRule.setCentralWidget(containerDatasetShow)

    windowRule.show()

def chooseDataSet():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog

    datasetFileName, _ = QFileDialog.getOpenFileName(QWidget(),"Choose a data set ... ", "D:\Amol\docs\Projects\Python\RuleProcessor\Datasets","All Files (*);;Python Files (*.py)", options=options)
    if datasetFileName:
        print(datasetFileName)
        f = open(str(datasetFileName), 'r', encoding="utf8")
        with f:
            numUserStories = sum(1 for line in f if line.rstrip())
            f.seek(0)
            userStoriesData = f.read()

        showDataSet(userStoriesData,numUserStories)

app = QApplication([])
window = QMainWindow()
window.setWindowTitle("RuleProcessor")
windowRule = QMainWindow()

layout = QGridLayout()

lblUserStory = QLabel("User Story")
vBoxLayoutUserStory = QVBoxLayout()

hBoxLayoutUserStory = QHBoxLayout()
txtUserStory = QLineEdit()
hBoxLayoutUserStory.addWidget(txtUserStory)

btnDataSet = QPushButton("...")
btnDataSet.setFixedSize(50,25)
hBoxLayoutUserStory.addWidget(btnDataSet)
btnDataSet.clicked.connect(lambda: chooseDataSet())

vBoxLayoutUserStory.addLayout(hBoxLayoutUserStory)

hBoxLayoutUserStoryButtons = QHBoxLayout()
hBoxLayoutUserStoryButtons.setAlignment(Qt.AlignLeft)
# hBoxLayoutUserStoryButtons.setGeometry(QRect(0,0,500,500))
btnGenerateFacts = QPushButton("Generate Facts")
btnGenerateFacts.setFixedSize(350,50)
# hBoxLayoutUserStoryButtons.addWidget(btnGenerateFacts)
btnGenerateFacts.clicked.connect(lambda: generateFacts("knowledgebases\kbUserStory.pl"))

btnShowFactsBase = QPushButton("Show Factsbase")
btnShowFactsBase.setFixedSize(250,30)
# btnShowFactsBase.setEnabled(False)
isFactsbaseGenerated = False
hBoxLayoutUserStoryButtons.addWidget(btnShowFactsBase)
btnShowFactsBase.clicked.connect(showFactsBase)

btnShowTypeDepGraph = QPushButton("Show Type Dependency Graph")
btnShowTypeDepGraph.setFixedSize(250,30)
hBoxLayoutUserStoryButtons.addWidget(btnShowTypeDepGraph)

isTypeDepGraphGenerated = False

btnShowTypeDepGraph.clicked.connect(showTypeDepGraph)

vBoxLayoutUserStory.addLayout(hBoxLayoutUserStoryButtons)

vBoxLayoutRuleButtons = QVBoxLayout()
btnRuleAdd = QPushButton("Add")
btnRuleUpdate = QPushButton("Update")
btnRuleDelete = QPushButton("Delete")
btnRuleExecute = QPushButton("Execute")
btnRuleShow = QPushButton("Show")

vBoxLayoutRuleButtons.addWidget(btnRuleAdd)
vBoxLayoutRuleButtons.addWidget(btnRuleUpdate)
vBoxLayoutRuleButtons.addWidget(btnRuleDelete)
vBoxLayoutRuleButtons.addWidget(btnRuleExecute)
vBoxLayoutRuleButtons.addWidget(btnRuleShow)

btnRuleAdd.clicked.connect(addRule)
btnRuleUpdate.clicked.connect(updateRule)
btnRuleDelete.clicked.connect(deleteRule)
btnRuleExecute.clicked.connect(executeRule)
btnRuleShow.clicked.connect(showRule)

lblKnowledgeBase = QLabel("Knowledge Base")
txtareaKnowledgeBase = QPlainTextEdit()
lblRules = QLabel("Extraction Rulebase")
tblRules = QTableWidget()

tblRules.setColumnWidth(0,100)
tblRules.setColumnWidth(1,500)
tblRules.setColumnWidth(2,3000)

populateRuleTable()

#tblRules.cellClicked.connect(ruleExecute)

btnExtract = QPushButton("Extract")
btnReset = QPushButton("Reset")
btnExit = QPushButton("Exit")
lblConceptualModel = QLabel("Conceptual Model")
txtareaConceptualModel = QPlainTextEdit()
txtareaConceptualModel.setReadOnly(True)
layout.addWidget(lblUserStory, 0, 0)
layout.addLayout(vBoxLayoutUserStory,0,1)
txtUserStory.setText("As a teacher, I want to mark attendance of student.")

# layout.addWidget(lblKnowledgeBase, 1, 0)
# layout.addWidget(txtareaKnowledgeBase, 1, 1)

layout.addWidget(lblRules, 2, 0)
# layout.addWidget(tblRules, 2, 1)
containerRuleButtons = QWidget()
containerRuleButtons.setLayout(vBoxLayoutRuleButtons)
hBoxLayoutRules = QHBoxLayout()
hBoxLayoutRules.addWidget(tblRules)
hBoxLayoutRules.addWidget(containerRuleButtons)

c = QWidget()
c.setLayout(hBoxLayoutRules)
layout.addWidget(c,2,1)

hBoxLayoutExtractionButtons = QHBoxLayout()

hBoxLayoutExtractionButtons.setAlignment(Qt.AlignRight)
btnExtract.setFixedSize(250,30)
btnReset.setFixedSize(250,30)
btnExit.setFixedSize(250,30)
hBoxLayoutExtractionButtons.addWidget(btnExtract)
hBoxLayoutExtractionButtons.addWidget(btnReset)
hBoxLayoutExtractionButtons.addWidget(btnExit)

layout.addLayout(hBoxLayoutExtractionButtons, 3, 1)

layout.addWidget(lblConceptualModel, 4, 0)
layout.addWidget(txtareaConceptualModel, 4, 1)
container = QWidget()
container.setLayout(layout)

window.setCentralWidget(container)

btnExtract.clicked.connect(extractConceptualModel)
btnReset.clicked.connect(doReset)
btnExit.clicked.connect(doExit)

window.show()

sys.exit(app.exec())
