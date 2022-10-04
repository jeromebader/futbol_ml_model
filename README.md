# Proyecto de data engineering

En el presente proyecto realizamos el desarrollo de una aplicación de Machine Learning End-to-End
con un caso de uso especifico.

El proyecto se desarrollo en un plazo acortado de 2 días. Se usaron las siguientes tecnologías:
- Python
- Flask
- MySql
- AWS RDS
- Python Anywhere
- CI/CD Github Pipeline
- HTML/CSS Bootstrap

Se uso una base de datos de Kaggle que se transformó debido al tamaño y el modelo.

## Base de Datos
https://www.kaggle.com/datasets/hugomathien/soccer

- +25,000matches
- +10,000players


## Endpoints:

- **/show_data [GET]**
  Muestra los ultimos datos agregados a la DB

- **/monitor_model [GET]**
  Endpoint que permite analizar el performace del modelo, esta llama al endpoint retrain

- **/app_model [GET]**
  Endpoint que genera el primer modelado de los datos

- **/uploads [POST]**
  Enpoint para subir JSON, llama al endpoint /ingest_data

- **/ingest_data [POST]**
  Endpoint que recoge la nueva informacion registrada desde llamada POST en formato JSON
  y guarda los datos en db MySQL. Hace validaciónes para prevenir injection SQL

- **/retrain [GET]**
  Endpoint que permite realizar un reentrenamiento en caso el score se más bajo.

- **/predict [GET]**
  Endpoint que realiza la predicción

- **/db_connect [GET]**
  Endpoint de prueba que conecta con la base de datos de AWS


## Frontend:

- **Index**
para llamar los Endpoints a través de butones. Permite subir JSON
- **Make Predictions**
Realiza prediciones a través del endpoint /predict
- **Retrain**
Realiza reentrenamiento del modelo a través del endpoint /retrain
- **Show Data**
Muestra los ultimos datps ingestados via API o upload