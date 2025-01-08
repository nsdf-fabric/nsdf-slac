create_env:
	@conda remove -n "slac" --all -y
	@conda create -n "slac" python==3.10 -y
	@echo "Installing dependencies..."
	@conda run -n slac pip install -r requirements.txt
dev:
	@panel serve slac.py --dev --show
build:
	@docker build . -t dashboard -f Dockerfile
run:
	@docker run --rm -p 10325:10325 dashboard
cpp:
	@g++ -o channel_extract channel_extract.cpp -L$$HOME/IOLibrary/lib -lcdmsio -I$$HOME/installroot/include -L$$HOME/installroot/lib -lCore -L$$HOME/installcnpy/lib -lcnpy -lz
download:
	@python download.py
genidx:
	@python idx.py
kill:
	@kill $$(lsof -i:10325)
