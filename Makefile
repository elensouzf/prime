CC=gcc
CFLAGS=-Wall -Wextra -O2

prime: prime.c
	$(CC) $(CFLAGS) -o prime prime.c

clean:
	rm -f prime
