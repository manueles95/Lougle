DROP TABLE Docs;
DROP TABLE Terms;
DROP TABLE InvertedIndex;
DROP TABLE Cluster
DROP TABLE WebPages;
DROP TABLE WebTerms;
DROP TABLE WebInvertedIndex;

CREATE TABLE Docs (idDoc INT NOT NULL, titulo VARCHAR(122), autor VARCHAR(122), abstract TEXT, clusterId INT,  PRIMARY KEY (idDoc), FOREIGN KEY (clusterid) REFERENCES Cluster(clusterid));

-- alter table docs where id = id para cambiar la clusterid para indicar que ahora pertence a un cluster????

CREATE TABLE Terms (term VARCHAR(122) NOT NULL, idf FLOAT, PRIMARY KEY (term));

CREATE TABLE TemporalTerms (term VARCHAR(122) NOT NULL, idf FLOAT, PRIMARY KEY (term));

CREATE TABLE InvertedIndex (idInverted INT NOT NULL AUTO_INCREMENT, IdDoc INT NOT NULL, Term VARCHAR(122) NOT NULL, tf INT, PRIMARY KEY (idInverted), FOREIGN KEY (IdDoc) REFERENCES Docs(idDoc));

CREATE TABLE Query (term VARCHAR(122) NOT NULL, tf INT NOT NULL, PRIMARY KEY (term));

CREATE TABLE Query1 (term VARCHAR(122) NOT NULL, tf INT NOT NULL, PRIMARY KEY (term));

CREATE TABLE Cluster (clusterid INT NOT NULL, nombre VARCHAR(122), pid INT, PRIMARY KEY (clusterid), FOREIGN KEY (pid) REFERENCES Cluster(clusterid));


-- webCrawler Tables
CREATE TABLE WebPages (idUrl VARCHAR(122) NOT NULL, url VARCHAR(255) NOT NULL, texto TEXT, PRIMARY KEY (idUrl));

CREATE TABLE WebTerms (term VARCHAR(122) NOT NULL, idf FLOAT, PRIMARY KEY (term));

CREATE TABLE WebInvertedIndex (idInverted INT NOT NULL AUTO_INCREMENT, IdUrl VARCHAR(122) NOT NULL, Term VARCHAR(122) NOT NULL, tf INT, PRIMARY KEY (idInverted), FOREIGN KEY (IdUrl) REFERENCES WebPages(idUrl));

-- Mybe no la ocupamos, si es que podemos hacer que docs ya pertenezca a un cluster
-- CREATE TABLE Document (id INT NOT NULL, nombre VARCHAR(122), clusterid INT, PRIMARY KEY (id), Foreign KEY (clusterid) REFERENCES Cluster(clusterid));

-- insert into Query values ("LISP", 1);

-- insert into Terms (select Term, log10(3/count(*)) from InvertedIndex group by Term);

-- select distinct IdDoc from InvertedIndex where Term = "arboles" or Term = "utiles";

-- select IdDoc from InvertedIndex i, Query q where i.Term = q.Term group by i.IdDoc having count(i.term) = (select count(*) from Query);


-- con esta query calculamos la relevancia de los documentos que contengan los terminos de la query
-- es necesario dividir los elementos de la query en tuplas diferentes por cada termino de la query 
-- insert into Query values ("arboles", 1);
-- insert into Query values ("utiles", 1);
-- de la misma manera que dividimos la consulta ^ de la tarea de los arboles
 
-- select i.IdDoc, sum(q.tf * t.idf * i.tf * t.idf) from Query q, InvertedIndex i, Terms t where q.term = t.term AND i.term = t.term group by i.IdDoc order by 2 desc;

-- CREATE TABLE Especimen (id INT NOT NULL, nombre VARCHAR(122), tid INT, PRIMARY KEY (id), Foreign KEY (tid) REFERENCES Taxon(tid));

-- CREATE TABLE Taxon (tid INT NOT NULL, nombre VARCHAR(122), pid INT, PRIMARY KEY (tid), FOREIGN KEY (pid) REFERENCES Taxon(tid));

-- insert into taxon values (1, "docUno", NULL);
-- insert into taxon values (33, "docTreintaytres", 1);

-- insert into especimen values (100, "docCien", 33);

-- insert into cluster values (1, "docTreintaytres", NULL);

-- select i.IdDoc, sum(q.tf * t.idf * i.tf * t.idf) from Query q, InvertedIndex i, Terms t where q.term = t.term AND i.term = t.term group by i.IdDoc order by 2 desc;