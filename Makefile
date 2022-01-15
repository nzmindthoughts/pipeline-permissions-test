.PHONY: test clean deploy

all:
	@echo "ERROR: noop"
	@exit 1

test:
	@python3 -m unittest discover
	@echo "OK: $@"

deploy:
	@echo "OK: $@"

clean:
	@for f in `find . -name '*.pyc'`;do rm -rf $$f; done
	@echo "OK: $@"
