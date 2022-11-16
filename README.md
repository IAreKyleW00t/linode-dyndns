# Linode DynDNS

A Python tool for dynamically updating Linode Domain Records, heavily based on [nvllsvm/linode-dynamic-dns](https://github.com/nvllsvm/linode-dynamic-dns) but I wanted something a bit more updated and built regularly.

I am by no means a Python expert, this is just something I made for fun.

## Usage

Full usage can be found using the `--help` flag. Each option has a matching env variable associated with it, ie: `DOMAIN`, `HOST`, `TOKEN`, etc. which can be set instead of setting flags on the cli tool itself.

```
Usage: linode_dyndns [OPTIONS]

  A Python tool for dynamically updating Linode Domain Records.

Options:
  --version               Show the version and exit.
  -v, --verbose           Display more output during Record updates.
  -d, --domain TEXT       Domain name as listed in your Linode Account (eg:
                          example.com).  [required]
  -h, --host TEXT         Host to create/update within the specified Domain
                          (eg: mylab).  [required]
  -t, --token TEXT        Linode API token  [required]
  -i, --interval INTEGER  Interval to recheck IP and update Records at (in
                          minutes).
  --ipv6                  Also create a AAAA (if possible).
  --help                  Show this message and exit.
```

You can also run it via Docker for ease-of-use

```sh
docker run --rm -it --name linode_dyndns \
    -e DOMAIN=exmaple.com \
    -e HOST=mylab \
    -e TOKEN=abc...789 \
    -e INTERVAL=15 \
    iarekylew00t/linode-dyndns
```

## Local development

The `requirements.txt` file is mainly for dependencies required for a developer, including stuff like the [black](https://github.com/psf/black) formatter.

Setup your local environmnet

```sh
git clone https://github.com/IAreKyleW00t/linode-dyndns.git
cd linode-dyndns
python3 -m venv .venv
source .venv/bin/activate
```

Install all the dependencies

```sh
pip install -r requirements.txt
```

## Building

You can build it normally via pip

```sh
pip install .
```

or build the Docker image instead

```sh
docker build -t linode-dyndns .
```

## License

See [LICENSE](LICENSE).

## Contributing

Feel free to contribute and make things better by opening an [Issue](https://github.com/IAreKyleW00t/linode-dyndns/issues) or [Pull Requests](https://github.com/IAreKyleW00t/linode-dyndns/pulls).
