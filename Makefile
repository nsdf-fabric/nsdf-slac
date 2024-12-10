run:
	@docker run --rm -p 10325:10325 slac

kill:
	@kill $$(lsof -i:10325)
