
cpp:
	@g++ -o channel_extract channel_extract.cpp -L$$HOME/IOLibrary/lib -lcdmsio -I$$HOME/installroot/include -L$$HOME/installroot/lib -lCore -L$$HOME/installcnpy/lib -lcnpy -lz
# workflows
download:
	@python download.py
genidx:
	@python idx.py
upload:
	@python upload.py

