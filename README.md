# Linode DynDNS

A Python tool for dynamically updating Linode Domain Records with your current IP address. Inspired by [nvllsvm/linode-dynamic-dns](https://github.com/nvllsvm/linode-dynamic-dns) but now utilizes the official [linode_api4](https://github.com/linode/linode_api4-python) package for Python.

Available on: [GitHub](https://github.com/IAreKyleW00t/linode-dyndns) | [DockerHub](https://hub.docker.com/r/iarekylew00t/linode-dyndns) | [PyPi](https://pypi.org/project/linode-dyndns/)

## Installation

You can install the tool by running

```sh
pip install linode-dyndns
```

Alternatively, you can use docker

```sh
docker pull iarekylew00t/linode-dyndns
```

## Usage

Full usage and defaults can be found using the `--help` flag. Each option has a matching env variable associated with it which can be set instead of setting flags on the cli tool itself, see the [Environment variables](#Environment-variables) section.

When running the tool in a loop (`--interval` flag), if for some reason the tool cannot get your IP during a run, it will skip it and retry during the next interval.

```sh
linode_dyndns \
  --domain exmaple.com \
  --host mylab \
  --token abc...789 \
  --interval 60
```

or, running it via Docker (which also supports passing flags)

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

You can build the package yourself via the [build](https://pypi.org/project/build/) module (included in `requirements.txt`)

```sh
python -m build --sdist --wheel --outdir dist/ .
```

or build the Docker image instead

```sh
docker build -t linode-dyndns .
```

## Contributing

Feel free to contribute and make things better by opening an [Issue](https://github.com/IAreKyleW00t/linode-dyndns/issues) or [Pull Requests](https://github.com/IAreKyleW00t/linode-dyndns/pulls).

### Code Styling

This tool is painted [black](https://github.com/psf/black) and has a corresponding [workflow](https://github.com/IAreKyleW00t/linode-dyndns/actions/workflows/black.yml) to enforce it. If you plan to contribute anything, please ensure you run `black` against your files first (included in `requirements.txt`).

```sh
black .
```

## License

See [LICENSE](https://github.com/IAreKyleW00t/linode-dyndns/blob/main/LICENSE).
