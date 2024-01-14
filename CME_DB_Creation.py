import sqlite3

conn = sqlite3.connect('cme.db')
c = conn.cursor()
c.execute("""DROP TABLE extraction_rules """)

c.execute("""CREATE TABLE extraction_rules (
            ruleid INTEGER Primary key,
            elementtype TEXT,
            consequent TEXT,
            antecedent TEXT
    )""")

all_rules = [
(1, "Class", "cls1(C)",	"noun(C)"),
(2, "Class", "cls2(C)",	"noun(C1),noun(C2),compound(C1,C2),atom_concat(C2,C1,C)"),
(3, "Data Property", "dataproperty1(DP,D,R)", "noun(DP),prep(DP,of),noun(L),pobj(of,L),(noun(M),(compound(L,M))->atom_concat(M,L,D);D=L),(R='String')"),
(4, "Data Property", "dataproperty2(DP,D,R)",  "adj(DP),noun(L),amod(L,DP),(noun(M),(compound(L,M))->atom_concat(M,L,D);D=L),(R='String')"),
(5, "Object Property", "objectproperty1(OP,D,R)",  "noun(X),noun(D),compound(X,D),atom_concat(D,X,R),atom_concat('has',X,OP)"),
(6, "Object Property", "objectproperty2(OP,D,R)",  "verb(OP),xcomp(want,OP),noun(P),pobj(as,P),(noun(Q),(compound(P,Q))->atom_concat(Q,P,D);D=P),noun(L),dobj(OP,L),(noun(M),(compound(L,M))->atom_concat(M,L,R);R=L)"),
(7, "Object Property", "objectproperty3(OP,D,R)",  "verb(V),adp(P),xcomp(want,V),noun(S),pobj(as,S),(noun(T),(compound(S,T))->atom_concat(T,S,D);D=S),noun(L),prep(V,P),pobj(P,L),(noun(M),(compound(L,M))->atom_concat(M,L,R);R=L),atom_concat(V,P,OP)"),
(8, "Object Property", "objectproperty4(OP,D,R)",  "verb(V),xcomp(want,V),noun(P),pobj(as,P),(noun(Q),(compound(P,Q))->atom_concat(Q,P,D);D=P),noun(X),adp(PRE),dobj(V,X),prep(X,PRE),noun(L),pobj(PRE,L),(noun(M),(compound(L,M))->atom_concat(M,L,R);R=L),atom_concat(V,X,O),atom_concat(O,PRE,OP)"),
(9, "Object Property", "objectproperty5(OP,D,R)",  "verb(V),verb(OP),(xcomp(want,V);ccomp(want,V)),advcl(V,OP),nsubj(OP,'i'),noun(P),pobj(as,P),(noun(Q),(compound(P,Q))->atom_concat(Q,P,D);D=P),noun(L),dobj(OP,L),(noun(M),(compound(L,M))->atom_concat(M,L,R);R=L)"),
(10, "Object Property", "objectproperty6(OP,D,R)",  "verb(V1),verb(V2),(xcomp(want,V1);ccomp(want,V1)),advcl(V1,V2),nsubj(V2,'i'),noun(P),pobj(as,P),(noun(Q),(compound(P,Q))->atom_concat(Q,P,D);D=P),noun(X),adp(PRE),dobj(V2,X),prep(X,PRE),noun(L),pobj(PRE,L),(noun(M),(compound(L,M))->atom_concat(M,L,R);R=L),atom_concat(V2,X,O),atom_concat(O,PRE,OP)"),
(11, "Object Property", "objectproperty7(OP,D,R)",  "verb(OP),advcl(want,OP),nsubj(OP,'i'),noun(P),pobj(as,P),(noun(Q),(compound(P,Q))->atom_concat(Q,P,D);D=P),noun(L),dobj(OP,L),(noun(M),(compound(L,M))->atom_concat(M,L,R);R=L)"),
(12, "Sub Class Of", "subclassof1(C,P)",  "noun(C1),noun(P),compound(P,C1),atom_concat(C1,P,C)"),
]

c.executemany("INSERT INTO extraction_rules (ruleid,elementtype,consequent,antecedent) VALUES (?, ?, ?, ?)", all_rules)

# select data
c.execute("SELECT * FROM extraction_rules")
# print(c.fetchall())

# processing data row by row
for row in c.fetchall():
    print("Rule Id:",row[0])
    print("Consequent:", row[2])
    print("Antecedent:", row[3])

# commit
conn.commit()

# close the connection
conn.close()