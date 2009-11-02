pyfiles := $(wildcard *.py)
docfiles := $(patsubst %.py,%.html,$(pyfiles))

all : doc

doc : $(docfiles)

%.html : %.py
	pydoc -w $(patsubst %.py,%,$^)

clean :
	rm *.html *.pyc
