cpp:
	@g++ -o channel_extract channel_extract.cpp -L$$HOME/IOLibrary/lib -lcdmsio -I$$HOME/installroot/include -L$$HOME/installroot/lib -lCore -L$$HOME/installcnpy/lib -lcnpy -lz
download:
	@python download.py
genidx:
	@python idx.py
dev:
	@panel serve slacidx.py --dev --show
publish:
	@panel serve slacidx.py --address='0.0.0.0' --allow-websocket-origin='*'  --port=10220
build:
	@docker build . -t dashboardidx -f Dockerfile.idx
run:
	@docker run --rm -p 10325:10325 slac
runidx:
	@docker run --rm -p 10001:10001 dashboardidx
kill:
	@kill $$(lsof -i:10325)
