all: binary

test:
	test -n "$(NETSCALER_HOST)"
	bats-core/bin/bats --pretty tests/bats

binary:
	pp \
	-o check_netscaler \
	-M LWP \
	-M LWP::Protocol::https \
	-M IO::Socket::SSL \
	-M JSON \
	-M URI::Escape \
	-M MIME::Base64 \
	-M Data::Dumper \
	-M Monitoring::Plugin \
	-M Time::Piece \
	-M PAR \
	check_netscaler.pl

clean:
	rm check_netscaler || true
