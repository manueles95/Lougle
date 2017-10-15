DROP TABLE Docs;
DROP TABLE Terms;
DROP TABLE InvertedIndex;

CREATE TABLE Docs (idDoc INT NOT NULL, titulo VARCHAR(122), autor VARCHAR(122), abstract TEXT, PRIMARY KEY (idDoc));

CREATE TABLE Terms (term VARCHAR(122) NOT NULL, idf FLOAT, PRIMARY KEY (term));

CREATE TABLE TemporalTerms (term VARCHAR(122) NOT NULL, idf FLOAT, PRIMARY KEY (term));

CREATE TABLE InvertedIndex (idInverted INT NOT NULL AUTO_INCREMENT, IdDoc INT NOT NULL, Term VARCHAR(122) NOT NULL, tf INT, PRIMARY KEY (idInverted), FOREIGN KEY (IdDoc) REFERENCES Docs(idDoc));

CREATE TABLE Query (term VARCHAR(122) NOT NULL, tf INT NOT NULL, PRIMARY KEY (term));

insert into Query values ("LISP", 1);

insert into Terms (select Term, log10(3/count(*)) from InvertedIndex group by Term);

-- select distinct IdDoc from InvertedIndex where Term = "arboles" or Term = "utiles";

-- select IdDoc from InvertedIndex i, Query q where i.Term = q.Term group by i.IdDoc having count(i.term) = (select count(*) from Query);


-- con esta query calculamos la relevancia de los documentos que contengan los terminos de la query
-- es necesario dividir los elementos de la query en tuplas diferentes por cada termino de la query 
-- insert into Query values ("arboles", 1);
-- insert into Query values ("utiles", 1);
-- de la misma manera que dividimos la consulta ^ de la tarea de los arboles
 
select i.IdDoc, sum(q.tf * t.idf * i.tf * t.idf) from Query q, InvertedIndex i, Terms t where q.term = t.term AND i.term = t.term group by i.IdDoc order by 2 desc;




