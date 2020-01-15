file per scaricare i dati INGV:

- Seismic_Network_IV_extraction.py: crea elenco stazioni disponibili su URL = "http://webservices.ingv.it/fdsnws/station/1/query?nodata=404&authoritative=any&level=station&net=IV"

- Stream_extraction.py: estrae traccia sismica dalla stazione disponibile più vicina

- main.py: estrae le tracce di tutti gli eventi elencati nel file data_for_ML.csv

- le tracce sismiche vengono salvate in file json separati nelle cartelle Store e Store_noise (solo sul drive)

- il file analysis.py crea il dataframe.json per la rete neurale, filtrando gli eventi che sono da scartare in base a alcuni parametri

Nella cartella cnn (Daniele):

- il file noise.py e signal.py creano le immagini per la cnn

- model.json contiene il modello della rete neurale

- il file cnn.py allena la rete neurale

