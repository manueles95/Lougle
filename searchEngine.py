import mysql.connector as mySQL
from tkinter import *
from tkinter import simpledialog
import re

def temporal():
	clearDBRecords()
	parse()

# Funcion para vaciar las tablase de la base de datos
def clearDBRecords():
	conn = mySQL.connect(user='root', password='root', database='textSearch')
	c = conn.cursor()

	c.execute("DELETE FROM InvertedIndex;")
	c.execute("DELETE FROM Terms;")
	c.execute("DELETE FROM Docs;")
	c.execute("DELETE FROM Cluster;")
	# c.execute("DELETE FROM Document;")	

	conn.commit()			
				
	print ("Data Base Cleared")

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
		print("Term Not Found")

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


# Funcion para hacer clustering de los documentos
def cluster():
	
	conn = mySQL.connect(user='root', password='root', database='textSearch')
	c = conn.cursor()

	c.execute("DELETE FROM Cluster;")
	conn.commit()	

	c.execute("select * from docs")

	# esta n se va a usar cuando necesitemos que la coleccion lea un numero no determinado de documentos
	documents = c.fetchall()
	n = len(documents)
	# print(n)

	matrix = [[0 for x in range(n)]for y in range(n)]

	# construimos la matriz de similitud
	# aqui cambiamos el 3 por n para hacerlo del tamano que sea
	for i in range(0, n):
		for j in range(0,n):
			c.execute("""select sum(i.tf * t.idf * j.tf * t.idf)
			from InvertedIndex i, InvertedIndex j, Terms t 
			where i.term = t.term AND j.term = t.term AND i.IdDoc = %s AND j.IdDoc = %s""", (i +1, j +1))

			similarity = c.fetchone()
			# print(int(similarity[0]))
			matrix[i][j] = similarity[0]
			# print(matrix[i][j])
		#end for
	#end for

	# Se crean los cluster iniciales con lo que se manipularan las cosas
	# Tambien se agregan los documentos iniciales a sus clusters
	for i in range(0,n):
		j= i+1 #para poder tener el id correcto le sumamos un 1 a la variable j
		clustername = "clusterNumero" + str(j)
		# print(clustername)
		c.execute("insert into cluster (clusterid, nombre, pid) values(%s, %s, NULL)", (j, clustername))

		c.execute("""UPDATE Docs
						SET clusterid = %s
						where idDoc = %s;""", (j,j))
	#End for
	conn.commit()
	
	# Primero voy a crear el cluster combinado inicial
	continuar = True
	iteration = 0
	while continuar == True:
		maxSim = 0
		for i in range(0, n):
			for j in range(0,n):
				if i != j:
					tempSim = matrix[i][j]
					# print(matrix[i][j])

					if tempSim > maxSim:
						maxSim = tempSim
						doc1 = i + 1
						doc2 = j + 1

		# eliminamos la similitud correspondiente a esos dos lugare ya que no se podran evaluar consigo mismos ya
		
		# print("******************")
		# print(doc1)
		# print(doc2)
		matrix[doc1 - 1][doc2 - 1] = 0
		matrix[doc2 - 1][doc1 - 1] = 0
		
		# primero sacamos el cluster mas alto del primer doc de la matriz
			
		c.execute("select clusterid from docs where idDoc = %s", [doc1])
		paso1 = int(c.fetchone()[0])
		# print(paso1)


		root = False
		while root == False:

			c.execute("select pid from cluster where clusterid = %s", [paso1])
			paso2 = c.fetchone()
			paso2if = str(paso2)

			if paso2if != "(None,)":
				# print("ahi vamos")
				paso2 = int(paso2[0])

				paso1 = paso2

				
			elif paso2if == "(None,)":
				root = True
				# print("ya llegamos al root")
				clustermerge1 = paso1



		# luego hacemos lo mismo para el segundo documento para agregarlo al cluster

		c.execute("select clusterid from docs where idDoc = %s", [doc2])
		step1 = int(c.fetchone()[0])
		# print(step1)


		root = False
		while root == False:

			c.execute("select pid from cluster where clusterid = %s", [step1])
			step2 = c.fetchone()
			step2if = str(step2)

			if step2if != "(None,)":
				# print("ahi vamos x2")
				step2 = int(step2[0])

				step1 = step2

				
			elif step2if == "(None,)":
				root = True
				# print("ya llegamos al root")
				clustermerge2 = step1




		if str(clustermerge1) != str(clustermerge2):
			print("////////////////################")
			print(clustermerge1)
			print(clustermerge2)

			c.execute("select clusterid from cluster")
			numeroDeCluster = len(c.fetchall()) + 1 # es el id del cluster nuevo que se va a crear 1 + el total de cluster que hay
			clustername = "clusterNumero" + str(numeroDeCluster)
			# print(numeroDeClusters)

			c.execute("insert into cluster (clusterid, nombre, pid) values(%s, %s, NULL)", (numeroDeCluster, clustername))

			c.execute("""UPDATE cluster
							SET pid = %s 
							WHERE clusterid = %s OR clusterid = %s""", (numeroDeCluster, clustermerge1, clustermerge2))

			conn.commit()




		# print(paso2)
		c.execute("select count(*) from cluster where pid IS NULL")
		stopNow = int(c.fetchone()[0])
		if stopNow == 1:
			continuar = False


	print("Clustering Done")
	# por ultimo juntamos los dos clusters restantes
	# c.execute("select clusterid")

		# c.execute("select clusterid from cluster")
		# numeroDeCluster = len(c.fetchall()) + 1 # es el id del cluster nuevo que se va a crear 1 + el total de cluster que hay
		# clustername = "clusterNumero" + str(numeroDeCluster)
		# # print(numeroDeClusters)

		# c.execute("insert into cluster (clusterid, nombre, pid) values(%s, %s, NULL)", (numeroDeCluster, clustername))

		# c.execute("""UPDATE cluster
		# 				SET pid = %s 
		# 				WHERE clusterid = %s OR clusterid = %s""", (numeroDeCluster, doc1, doc2))

		# conn.commit()


		# print("[ " + str(doc1) + " ] [ " + str(doc2) + " ]")

		# print(maxSim)
		# print(doc1)
		# print(doc2)



	# # aqui empiezo a iterar en el arbol creo que lo tengo que hacer en un while


	# c.execute("""select clusterid
	# 				from cluster
	# 				where pid IS NULL """)

	# result = c.fetchall()
	# i = 0
	# j = 0
	# for cluster in result:

	# 	papi = int(cluster[0])
	# 	print("papi" + str(int(cluster[0])))

	# 	c.execute("select count(*) from cluster where pid = %s", [papi])
	# 	resultado = c.fetchone()

	# 	if resultado[0] == 0:
	# 		node = int(cluster[0])
	# 		c.execute("""select idDoc
	# 						from docs 
	# 						where clusterid = %s""", [node])

	# 		leaf = c.fetchone()
		
	# 	elif resultado[0] == 1:


	# 		# print(leaf[0])

	# 	print(resultado[0])


	# getHighiestSimilarity(matrix)

	# guardando codigo por si la cago
	# # Primero voy a crear el cluster combinado inicial
	# maxSim = 0
	# for i in range(0, n):
	# 	for j in range(0,n):
	# 		if i != j:
	# 			tempSim = matrix[i][j]
	# 			# print(matrix[i][j])

	# 			if tempSim > maxSim:
	# 				maxSim = tempSim
	# 				doc1 = i + 1
	# 				doc2 = j + 1

	# # print(maxSim)
	# # print(doc1)
	# # print(doc2)

	# c.execute("select clusterid from cluster")
	# numeroDeCluster = len(c.fetchall()) + 1 # es el id del cluster nuevo que se va a crear 1 + el total de cluster que hay
	# clustername = "clusterNumero" + str(numeroDeCluster)
	# # print(numeroDeClusters)

	# c.execute("insert into cluster (clusterid, nombre, pid) values(%s, %s, NULL)", (numeroDeCluster, clustername))

	# c.execute("""UPDATE cluster
	# 				SET pid = %s 
	# 				WHERE clusterid = %s OR clusterid = %s""", (numeroDeCluster, doc1, doc2))

	# conn.commit()



def getHighiestSimilarity(matrix):
	
	for m in matrix:
		print(m)

	# while numero de clusetrs > 2;



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

		c.execute("select titulo from Docs where idDoc = %s", [docs[0]])
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

	c.execute("delete from Query;")
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
	c.execute("delete from Query1;")
	c.execute("delete from TemporalTerms")
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
				where q.term = t.Term AND i.term = t.Term 
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


	# result = c.fetchmany(size=10)
	result = c.fetchall()

	for r in result:
		print(r)

	# una vez con los id de la consulta de similitud se usa un select para extraer los documentos de la tabla docs con los ids que queremos
	documents = []
	for docs in result:

		c.execute("select titulo from Docs where idDoc = %s", [docs[0]])
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


	c.execute("delete from Query1;")
	c.execute("delete from TemporalTerms")
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
	

	# ------------------------------------------------------------------------>>>>>>>>>>>>>> puedes comentar de aqui para abajo


	# sea abre el archivo cacm.all y se guarda en "collection"
	collection = open('cacmmod5.all', 'r')
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

			
			a = a.lower()
			# a = a.replace("\n", " ")
			a = a.replace(",", " ")
			# a = a.replace("' ", " ")
			# a = a.replace(" '", " ")
			# a = a.replace("-", " ")
			a = a.replace(".", " ")
			a = a.replace(";", " ")
			a = a.replace(":", " ")
			a = a.replace("(", " ")
			a = a.replace(")", " ")
			a = a.replace("?", " ")
			a = a.replace("/", " ")
			a = a.replace("\"", " ")
			a = a.replace("["," ")
			a = a.replace("]"," ")
			a = a.replace("{"," ")
			a = a.replace("}"," ")

			aSet = set(a.split())
			for term in aSet:
				term = term.strip("'")
				term = term.strip()

				textCount = w.count(str(term))

				if (textCount > 0):
					df = {"docID" : document ["id"], "term": term, "tf": textCount}
					my_tf.append(df)
			s = s.union(set(tSet))
			s = s.union(set(aSet))
			# print("Each set")
			# print(tSet)
			# print(aSet)
	# collection.close()
	# Para corregir los id de los documentos y no tener errores de integridad utilizamos idcorrection para sumar los id's ya cargados a la tabla y continuar desde ese numero
	idCorrection = len(docs)

	# # #--------------------------------------------------------------------------------------->>>>>>>>puedes comentar de aqui para arriba

	tfile = open('LISAmod5.001', 'r')
	if tfile != None:
		## Del archivo extrae idDoc, text y terms
		docs = tfile.read().split("********************************************")
		del docs[-1] #borra el ultimo elemento vacio de la lista
		# print ('valor docs: ' + str(docs))
		# print ('len docs: ' + str(len(docs)))


		for doc in docs:			
			text = ''
			title = ''
			lines = doc.split("\n\n")
			# title = doc.split("\n\n")
			# print ('parsing file..' + doc)



			for line in lines:
				if line.find("Document") != -1:
					temp = int(line.split()[1]) + idCorrection
					docid = str(temp)
					title = line.split("\n")[2]
					# print(title)
				else:
					text += line+'\n'

			document = { "id":docid, "titulo":title, "texto":text, "autor":''}
			# print(document)
			my_docs.append(document)
			# print ('len de my_docs: ' + str(len(my_docs)))
			
			text = text.lower()
			text = text.replace("\n", " ")
			text = text.replace(",", " ")
			text = text.replace("' ", " ")
			text = text.replace(" '", " ")
			text = text.replace("-", " ")
			text = text.replace(".", " ")
			text = text.replace(";", " ")
			text = text.replace(":", " ")
			text = text.replace("(", " ")
			text = text.replace(")", " ")
			text = text.replace("?", " ")
			text = text.replace("/", " ")
			text = text.replace("\"", " ")
			text = text.replace("["," ")
			text = text.replace("]"," ")
			text = text.replace("{"," ")
			text = text.replace("}"," ")
			t = set(text.split())
			for term in t:
				term = term.strip("'")
				term = term.strip()
				textCount = text.count(str(term))
				
				if (textCount > 0):
					df = {"docID" : document ["id"], "term": term, "tf": textCount}
					my_tf.append(df)
			s = s.union(set(t))



		# s = sorted(s)
		# print("my_tf")
		# print(my_tf[0])
		# print(my_docs[0])
		# print(lines)
		# print(s)
		# print ('len de my_docs: ' + str(len(my_docs)))
		# print (len(s))

		# for tf in my_tf:
		# 	print(tf)

		#----------------------------------------------------------------------------->>>>>>>>puedes comentar de aqui para arriba X2


	collection = open('CISImod5.all', 'r')
	idCorrection = idCorrection *2
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
				elif line.find('.A') != -1 and len(line) <= 2 or line.find('.B') != -1 and len(line) <= 2:
					copyT = False
				elif copyT:
					# print(line + '\n')
					t = line

				if line.find('.W') != -1 and len(line) <= 2:
					copyW = True
				elif line.find('.X') != -1 and len(line) <= 2:
					copyW = False
				elif copyW:
					# print(line + '\n')
					w += '\n' + line
				
				if line.find('.A') != -1 and len(line) <= 2:
					copyA = True
				elif line.find('.W') != -1 and len(line) <= 2:
					copyA = False
				elif copyA:
					# print(line + '\n')
					a = line

			# print(t)
			# print(w)
			# print(a)
			# # print(len(lines))
			# print('\n')

			document = {"id":i + idCorrection, "titulo":t,"texto":w,"autor":a}
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

			
			a = a.lower()
			# a = a.replace("\n", " ")
			a = a.replace(",", " ")
			# a = a.replace("' ", " ")
			# a = a.replace(" '", " ")
			# a = a.replace("-", " ")
			a = a.replace(".", " ")
			a = a.replace(";", " ")
			a = a.replace(":", " ")
			a = a.replace("(", " ")
			a = a.replace(")", " ")
			a = a.replace("?", " ")
			a = a.replace("/", " ")
			a = a.replace("\"", " ")
			a = a.replace("["," ")
			a = a.replace("]"," ")
			a = a.replace("{"," ")
			a = a.replace("}"," ")

			aSet = set(a.split())
			for term in aSet:
				term = term.strip("'")
				term = term.strip()

				textCount = w.count(str(term))

				if (textCount > 0):
					df = {"docID" : document ["id"], "term": term, "tf": textCount}
					my_tf.append(df)
			s = s.union(set(tSet))
			s = s.union(set(aSet))
			# print("Each set")
			# print(tSet)
			# print(aSet)
	# collection.close()





	
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
parseButt = Button(toolbar, text='TEMP', command=temporal)
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
searchButt = Button(toolbar, text='Cluster', command=cluster)
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