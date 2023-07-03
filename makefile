CC=clang

CFLAGS= -std=c99 -Wall -pedantic

LDFLAGS=-shared

LIBS=-lm

PYTHON_INCLUDE_PATH = /usr/include/python3.7m

PYTHON_LANGUAGE_LIBRARY_PATH = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu

all: _molecule.so



libmol.so: mol.o
	$(CC) mol.o $(LDFLAGS) -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -fPIC -c  mol.c

_molecule.so: molecule_wrap.o libmol.so
	$(CC) -shared molecule_wrap.o -L. -lmol -L$(PYTHON_LANGUAGE_LIBRARY_PATH) -lpython3.7m -o _molecule.so

molecule_wrap.c: molecule.i mol.h
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -I$(PYTHON_INCLUDE_PATH)  -fPIC -o molecule_wrap.o

clean:
	rm -f *.o *.so molecule_wrap.c


