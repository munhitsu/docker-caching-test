default: context.tar test

context.tar:
	cd context && tar -cf ../context.tar .

test:
	python test.py
