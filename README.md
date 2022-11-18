# Linode DynDNS

A Python tool for dynamically updating Linode Domain Records with your current, inspired by [nvllsvm/linode-dynamic-dns](https://github.com/nvllsvm/linode-dynamic-dns) but now utilizes the official [linode_api4](https://github.com/linode/linode_api4-python) for Python.

## Usage

Full usage and defaults can be found using the `--help` flag. Each option has a matching env variable associated with it which can be set instead of setting flags on the cli tool itself, see the [Environment variables](#Environment-variables) section.

```
Usage: linode_dyndns [OPTIONS]

  A Python tool for dynamically updating Linode Domain Records with your
  current IP.

Options:
  --version               Show the version and exit.
  -d, --domain TEXT       Domain name as listed in your Linode Account (eg:
                          example.com).  [required]
  -h, --host TEXT         Host to create/update within the specified Domain
                          (eg: mylab).  [required]
  -t, --token TEXT        Linode API token  [required]
  -i, --interval INTEGER  Interval to recheck IP and update Records at (in
                          minutes).  [default: 0]
  -6, --ipv6              Also create a AAAA record (if possible).
  --ipv4-url TEXT         URL to use for getting public IPv4 address
                          [default: https://ipv4.icanhazip.com]
  --ipv6-url TEXT         URL to use for getting public IPv6 address
                          [default: https://ipv6.icanhazip.com]
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

### Environment variables

| Name       | Flag         |
| ---------- | ------------ |
| `VERBOSE`  | `--verbose`  |
| `DOMAIN`   | `--domain`   |
| `HOST`     | `--host`     |
| `TOKEN`    | `--token`    |
| `INTERVAL` | `--interval` |
| `IPV6`     | `--ipv6`     |
| `IPV4_URL` | `--ipv4-url` |
| `IPV6_URL` | `--ipv6-url` |

## Local development

The `requirements.txt` file is mainly for dependencies required for a developer, including stuff like the [black](https://github.com/psf/black) formatter.

Setup your local environmnet (ensure you are using Python 3.9 or newer)

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

See [LICENSE](https://github.com/IAreKyleW00t/linode-dyndns/blob/main/LICENSE).

## Contributing

Feel free to contribute and make things better by opening an [Issue](https://github.com/IAreKyleW00t/linode-dyndns/issues) or [Pull Requests](https://github.com/IAreKyleW00t/linode-dyndns/pulls).
