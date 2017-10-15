import mysql.connector as mySQL
from tkinter import *
from tkinter import simpledialog

# Funcion para vaciar las tablase de la base de datos
def clearDBRecords():
	conn = mySQL.connect(user='root', password='root', database='textSearch')
	c = conn.cursor()

	c.execute("DELETE FROM InvertedIndex;")
	c.execute("DELETE FROM Terms;")
	c.execute("DELETE FROM Docs;")	

	conn.commit()			
				
	print ("Data Base cleared")

# Funcion para buscar un termino en la base de datos
def searchTerm():
	textToSearch = simpledialog.askstring("textToSearch", "Intruduce termino a buscar:")

	# connecting to the db.
	conn = mySQL.connect(user='root', password='root', database='textSearch')
	c = conn.cursor()


	c.execute("SELECT * FROM Terms WHERE term = %s", [textToSearch])

	if c.rowcount:
		print (c.rowcount)
		textarea.delete(1.0, END)
		textarea.insert(END, "Term\t\t|IDF\n")
		for rows in c.fetchall() :
			print (rows)
			textarea.insert(END, str(rows[0]) + "\t\t|" +str(rows[1]))
	else :
		print("Term not found")

# Funcion para buscar un termino en un documento
def searchInDoc():
	# connecting to the db.
	conn = mySQL.connect(user='root', password='root', database='textSearch')
	c = conn.cursor()

	textToSearch = simpledialog.askstring("textToSearch", "Intruduce el id de documento suido por el termino: idDoc,term")

	idDoc, termino = textToSearch.split(',')
	# print (idDoc)

	c.execute("SELECT IdDoc, Term, tf from InvertedIndex where IdDoc = %s and Term = %s", [idDoc, termino])

	if c.rowcount:
		textarea.delete(1.0, END)
		textarea.insert(END, "IdDoc\t\tTerm\t\t|TF\n")
		for rows in c.fetchall() :
			print (rows)
			textarea.insert(END, str(rows[0]) + "\t\t|" +str(rows[1]) + "\t\t|" +str(rows[2]))
	else :
		print("Term not found")

# Funcion para buscar el DF del termino ingresado
def searchTermDF():
	textToSearch = simpledialog.askstring("textToSearch", "Intruduce termino a buscar:")

	# connecting to the db.
	conn = mySQL.connect(user='root', password='root', database='textSearch')
	c = conn.cursor()

	c.execute("select term, count(*) from InvertedIndex where Term = %s", [textToSearch])

	if c.rowcount:
		textarea.delete(1.0, END)
		textarea.insert(END, "Term\t\t|DF\n")
		for rows in c.fetchall() :
			print (rows)
			textarea.insert(END, str(rows[0]) + "\t\t|" +str(rows[1]))
	else :
		print("Term not found")

# Funcion procesa la query ingresada por el usuario y regresa los documentos 
#  ordenados de mayor a menor similitud
def query():

	qtf = []

	conn = mySQL.connect(user='root', password='root', database='textSearch')
	c = conn.cursor()

	c.execute("delete from Query;")
	conn.commit()

	textToSearch = simpledialog.askstring("textToSearch", "Introduce la consulta:")
	textToSearch = str(textToSearch)
	textToSearch = textToSearch.lower()
	textToSearch = textToSearch.replace("."," ")
	textToSearch = textToSearch.replace(","," ")
	textToSearch = textToSearch.replace("?"," ")
	textToSearch = textToSearch.replace("!"," ")
	textToSearch = textToSearch.replace("/"," ")
	textToSearch = textToSearch.replace("-"," ")
	textToSearch = textToSearch.replace("_"," ")
	textToSearch = textToSearch.replace("("," ")
	textToSearch = textToSearch.replace(")"," ")
	textToSearch = textToSearch.replace(":"," ")
	textToSearch = textToSearch.replace(";"," ")	
	textToSearch = textToSearch.strip()

	query = textToSearch.split()

	tSet = set(query)

	for term in tSet:
		textCount = query.count(str(term))

		if (textCount > 0):
			df = {"term": term, "tf": textCount}
			qtf.append(df)

	for tf in qtf:
		c.execute("INSERT INTO Query (term, tf) VALUES(%s,%s)", (tf["term"], tf["tf"]))

	conn.commit()

	c.execute("""select i.IdDoc, sum(q.tf * t.idf * i.tf * t.idf) 
				from Query q, InvertedIndex i, Terms t 
				where q.term = t.term AND i.term = t.term 
				group by i.IdDoc order by 2 desc;""")


	#result = c.fetchmany(size=10)
	result = c.fetchall()

	documents = []
	for docs in result:

		c.execute("select titulo from docs where idDoc = %s", [docs[0]])
		doc = c.fetchall()
		documents.append(doc)
	
	textarea.delete(1.0, END)
	textarea.insert(END, "Resultado de la Busqueda" + "\n\n")
	count = 0
	for rows in documents :
		textarea.insert(END,str(rows[0]) + "\n")
		count = count + 1
		if (count > 9) :
			break

	c.execute("delete from query;")
	conn.commit()

	print("Query Done")

	# asi es como se imprimia antes, unicamente el id de los docuemtnos con su similitud
	# count = 0
	# textarea.delete(1.0, END)
	# textarea.insert(END, "Doc ID\t\t|Simulitud\n")
	# for rows in result :
	# #for rows in c.fetchall() :

	# 	textarea.insert(END, str(rows[0]) + "\t\t|" +str(rows[1]) + "\n")
	# 	count = count + 1
	# 	if (count > 9) :
	# 		break

	


def queryDecHi():
	qtf = []

	conn = mySQL.connect(user='root', password='root', database='textSearch')
	# c = conn.cursor()
	c = conn.cursor(buffered=True)

	c.execute("delete from Query;")
	c.execute("delete from query1;")
	c.execute("delete from temporalTerms")
	conn.commit()

	textToSearch = simpledialog.askstring("textToSearch", "Introduce la consulta:")
	textToSearch = str(textToSearch)
	textToSearch = textToSearch.lower()
	textToSearch = textToSearch.replace("."," ")
	textToSearch = textToSearch.replace(","," ")
	textToSearch = textToSearch.replace("?"," ")
	textToSearch = textToSearch.replace("!"," ")
	textToSearch = textToSearch.replace("/"," ")
	textToSearch = textToSearch.replace("-"," ")
	textToSearch = textToSearch.replace("_"," ")
	textToSearch = textToSearch.replace("("," ")
	textToSearch = textToSearch.replace(")"," ")
	textToSearch = textToSearch.replace(":"," ")
	textToSearch = textToSearch.replace(";"," ")	
	textToSearch = textToSearch.strip()

	query = textToSearch.split()

	tSet = set(query)

	for term in tSet:
		textCount = query.count(str(term))

		if (textCount > 0):
			df = {"term": term, "tf": textCount}
			qtf.append(df)

	for tf in qtf:
		c.execute("INSERT INTO Query (term, tf) VALUES(%s,%s)", (tf["term"], tf["tf"]))
		# print(tf)

	conn.commit()

	c.execute("""select i.IdDoc, sum(q.tf * t.idf * i.tf * t.idf) 
				from Query q, InvertedIndex i, Terms t 
				where q.term = t.term AND i.term = t.term 
				group by i.IdDoc order by 2 desc;""")

	# ?? result = {"idDoc": idDoc, "sim": similitud}
	result = c.fetchall()

	# se obtienen los tres resultados "relevantes" de todos los obtenidos (primeros 3)
	resultR = result[0:3]

	# se obtiene el resultado "no relevante" - ultimo de los obtenidos
	resultS = result[-1]

	# necesario para generar los selects de los terminos con el sql de abajo
	fresult = [] 

	# aqui extraemos solo los id de ResultR para no preocuparnos de la similitud
	for idDoc in resultR:
		fresult.append(idDoc[0])

	# aqui sacamos los 5 terminos mas pesados del primer documento
	c.execute("""SELECT t.term, idf
				FROM terms t, InvertedIndex i
				WHERE t.term = i.term
				AND idDoc = %s
				ORDER BY idf desc """, [fresult[0]])
	
	# esos 5 terminos se guradan en en arreglo r1
	r1 = c.fetchmany(size = 5)
	# aqui sacamos los 5 terminos mas pesados del segundo documento
	c.execute("""SELECT t.term, idf
				FROM terms t, InvertedIndex i
				WHERE t.term = i.term
				AND idDoc = %s
				ORDER BY idf desc """, [fresult[1]])
	
	# esos 5 terminos se guradan en en arreglo r2
	r2 = c.fetchmany(size = 5)
	# aqui sacamos los 5 terminos mas pesados del terecer documento
	c.execute("""SELECT t.term, idf
				FROM terms t, InvertedIndex i
				WHERE t.term = i.term
				AND idDoc = %s
				ORDER BY idf desc """, [fresult[2]])
		
	# esos 5 terminos se guradan en en arreglo r3
	r3 = c.fetchmany(size = 5)
	# aqui sacamos los 5 terminos mas pesados del documento menos importante en este caso el ultimo
	c.execute("""SELECT t.term, idf
				FROM terms t, InvertedIndex i
				WHERE t.term = i.term
				AND idDoc = %s
				ORDER BY idf desc """, [resultS[0]])
	
	# los terminos se guardan en s1
	s1 = c.fetchmany(size = 5)
	# ya tengo r1, r2 y r3 para comparar los terminos y recalcular los pasos
	
	#aqui se guardan todos los terminos con sus pesos para hacer la tabla TemporalTerms
	finalset = []
	# los siguientes for construyen las tuplas para agregarselas a final step, con el cual se egeneraran la nuevas tablas temporales
	for t in r1:
		tp = {"term": t[0], "weight": t[1]}
		finalset.append(tp)
	
	for t in r2:
		tp = {"term": t[0], "weight": t[1]}
		finalset.append(tp)

	for t in r3:
		tp = {"term": t[0], "weight": t[1]}
		finalset.append(tp)

	# como la query no contiene los pesos de los terminos es necesario utilizar sql para extrar esos terminos de otra tabal diferente
	for t in qtf:
			c.execute("select idf from terms where term = %s", [t["term"]])
			weight = c.fetchone()
			if weight != None:
				tpq = {"term": t["term"], "weight": weight[0]}
				finalset.append(tpq)
			else:
				tpq = {"term": t["term"], "weight": 1}
				finalset.append(tpq)



	temporalTerms = [] # este arreglo se usara para guardar los terminos que se agregaran a la tabla TemporaTerms
	q1 = [] # arreglo para guardar los terminos que iran en la tabla query1
	
	for term in finalset:
		count = 0

		for t in qtf:
			if term["term"] == t["term"]:
				count = count + 1

		for t in r1:
			if term["term"] == t[0]:
				count = count + 1

		for t in r2:
			if term["term"] == t[0]:
				count = count + 1

		for t in r3:
			if term["term"] == t[0]:
				count = count + 1

		for t in s1:
			if term["term"] == t[0]:
				count = count - 1

		tp = {"term": term["term"], "weight": term["weight"]*count} #agregamso los terminos y sus pesos dependeiendo de cuantas veces se obtenga un termino en los nuevos terminos
		temporalTerms.append(tp)

		queryTuple = {"term": term["term"], "tf": count} # poblamos la tabla query1 con el termino y su frecuencia de termino
		q1.append(queryTuple)

	for term in temporalTerms: #se pobla la tabla temporal terms
		c.execute("INSERT INTO TemporalTerms (term, idf) VALUES(%s,%s)", [term["term"], term["weight"]])

	for term in q1: #se pobla la tabla query1
		c.execute("INSERT INTO Query1 (term, tf) VALUES(%s,%s)", [term["term"], term["tf"]])

	conn.commit()

	# comando sql para obtener la similitud entre la consulta y los documentos
	c.execute("""select i.IdDoc, sum(q.tf * t.idf * i.tf * t.idf) 
				from Query1 q, InvertedIndex i, TemporalTerms t 
				where q.term = t.term AND i.term = t.term 
				group by i.IdDoc order by 2 desc;""")


	result = c.fetchmany(size=10)

	# una vez con los id de la consulta de similitud se usa un select para extraer los documentos de la tabla docs con los ids que queremos
	documents = []
	for docs in result:

		c.execute("select titulo from docs where idDoc = %s", [docs[0]])
		doc = c.fetchall()
		documents.append(doc)
	
	textarea.delete(1.0, END)
	textarea.insert(END, "Resultado de la Busqueda" + "\n\n")
	count = 0
	for rows in documents :
		textarea.insert(END,str(rows[0]) + "\n")
		count = count + 1
		if (count > 9) :
			break


	c.execute("delete from query1;")
	c.execute("delete from temporalTerms")
	conn.commit();

	print("Query Done")


# Funcion que procesa la coleccion y la guarda en la base de datos
def parse():
	# arreglos en los que se almacenaran los valores a guardar
	my_docs = []
	my_tf = []
	doc_counts = []
	tfs = []

	s=set()
	# sea abre el archivo cacm.all y se guarda en "collection"
	collection = open('cacmMOD.all', 'r')
	# print ('valor tfile: ' + str(collection)
	i = 1
	# se dividen la coleccion en documentos, cada que hay un .I es un nuevo doc
	if collection != None:
		docs = collection.read().split(".I ")
		# print (docs)
		del docs[0]

		for doc in docs:
			# print(doc)
			t = ''
			w = ''
			a = ''
			copyT = False
			copyW = False
			copyA = False
			# copy = False
			lines = doc.splitlines()
			for line in lines:
				if line.find('.T') != -1 and len(line) <= 2:
					copyT = True
				elif line.find('.W') != -1 and len(line) <= 2 or line.find('.B') != -1 and len(line) <= 2:
					copyT = False
				elif copyT:
					# print(line + '\n')
					t = line

				if line.find('.W') != -1 and len(line) <= 2:
					copyW = True
				elif line.find('.B') != -1 and len(line) <= 2:
					copyW = False
				elif copyW:
					# print(line + '\n')
					w += '\n' + line
				
				if line.find('.A') != -1 and len(line) <= 2:
					copyA = True
				elif line.find('.N') != -1 and len(line) <= 2:
					copyA = False
				elif copyA:
					# print(line + '\n')
					a = line

			# print(t)
			# print(w)
			# print(a)
			# # print(len(lines))
			# print('\n')
			
			document = {"id":i,"titulo":t,"texto":w,"autor":a}
			i+=1
			my_docs.append(document)
			# print("Each document")
			# print(document)
			# Se limpia el texto para poder procesar las palabras
			w = w.lower()
			# w = w.replace("\n", " ")
			w = w.replace(",", " ")
			w = w.replace("' ", " ")
			w = w.replace(" '", " ")
			w = w.replace("-", " ")
			w = w.replace(".", " ")
			w = w.replace(";", " ")
			w = w.replace(":", " ")
			w = w.replace("(", " ")
			w = w.replace(")", " ")
			w = w.replace("?", " ")
			w = w.replace("/", " ")
			w = w.replace("\"", " ")
			w = w.replace("["," ")
			w = w.replace("]"," ")
			w = w.replace("{"," ")
			w = w.replace("}"," ")

			tSet = set(w.split())
			for term in tSet:
				term = term.strip("'")
				term = term.strip()

				textCount = w.count(str(term))

				if (textCount > 0):
					df = {"docID" : document ["id"], "term": term, "tf": textCount}
					my_tf.append(df)

			s = s.union(set(tSet))
			# print("Each set")
			# print(tSet)
	# collection.close()

		s = sorted(s)
		# print("my_tf")
		# print(my_tf)
		# print(s)
		# print ('len de my_docs: ' + str(len(my_docs)))
		# print (len(s))
	
		# nos conectamos a la base de datos
		conn = mySQL.connect(user='root', password='root', database='textSearch')
		c = conn.cursor()

		# se ingresan los valores extraidos del archivo a la base de datos
		try:
			for doc in my_docs:
				c.execute("INSERT INTO Docs (idDoc, titulo, autor, abstract) VALUES(%s,%s,%s,%s)", (doc["id"], doc["titulo"], doc["autor"], doc["texto"]))

			for tf in my_tf:
				c.execute("INSERT INTO InvertedIndex (IdDoc, Term, tf) VALUES(%s,%s,%s)", (tf["docID"], tf["term"], tf["tf"]))

			c.execute("INSERT INTO Terms (SELECT Term, LOG10(3204/COUNT(*)) FROM InvertedIndex GROUP BY Term)")
		
			conn.commit()
		except Exception as e:
			print ("IntegrityError")

	print("Data Base Loaded")

# parse()


# ventana
root = Tk()
root.wm_title("LOUGLE")
root.minsize(width=300, height=250)

# menu
menu = Menu(root)
root.config(menu=menu)

subMenu = Menu(menu)
menu.add_cascade(label='File', menu=subMenu)
subMenu.add_command(label='Clear DB', command=clearDBRecords)
# subMenu.add_command(label='Now...', command=doNothing)
# subMenu.add_separator()
# subMenu.add_command(label='Exit', command=doNothing)

# editMenu = Menu(menu)
# menu.add_cascade(label='Edit', menu=editMenu)
# editMenu.add_command(label='Redo', command=doNothing)

# text box
textarea = Text(root)
textarea.pack(expand=True, fill='both')
# textarea.insert(END, "Ora")

# toolbar
toolbar = Frame(root)

parseButt = Button(toolbar, text='Load collection', command=parse)
parseButt.pack(side=LEFT, padx=2, pady=2)
parseButt = Button(toolbar, text='Clear collection', command=clearDBRecords)
parseButt.pack(side=LEFT, padx=2, pady=2)
# printButt = Button(toolbar, text='Search in doc', command=searchInDoc)
# printButt.pack(side=RIGHT, padx=2, pady=2)
# searchButt = Button(toolbar, text='Search Term', command=searchTerm)
# searchButt.pack(side=RIGHT, padx=2, pady=2)
# searchButt = Button(toolbar, text='Term DF', command=searchTermDF)
# searchButt.pack(side=RIGHT, padx=2, pady=2)
searchButt = Button(toolbar, text='Query DecHi', command=queryDecHi)
searchButt.pack(side=RIGHT, padx=2, pady=2)
searchButt = Button(toolbar, text='Query', command=query)
searchButt.pack(side=RIGHT, padx=2, pady=2)
# entryText = StringVar()
# entry = Entry(toolbar, textvariable=entryText)
# entry.pack(side=RIGHT, padx=2)


toolbar.pack(side=TOP, fill=X)

# status bar

status = Label(root, text='Lougle', bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)

# # message vox
# tkMessageBox.showinfo('Window Title', 'Monkeys can live up to 300 years.')

# answer = tkMessageBox.askquestion('Question 1', 'Do you like silly faces?')
# if answer == 'yes':
# 	print('>:|')

###
###

root.mainloop()