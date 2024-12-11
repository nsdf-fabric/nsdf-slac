cpp:
	@g++ -o channel_extract channel_extract.cpp -L$$HOME/IOLibrary/lib -lcdmsio -I$$HOME/installroot/include -L$$HOME/installroot/lib -lCore -L$$HOME/installcnpy/lib -lcnpy -lz
download:
	@python download.py
genidx:
	@python idx.py
panel:
	@panel serve testidx.py --dev --show
run:
	@docker run --rm -p 10325:10325 slac
kill:
	@kill $$(lsof -i:10325)
