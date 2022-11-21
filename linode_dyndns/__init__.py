import platform
import os
import time
from pathlib import Path

import click
import requests
from linode_api4 import LinodeClient, Domain, DomainRecord

from linode_dyndns.version import version as __version__

COMPILED = Path(__file__).suffix in (".pyd", ".so")


def get_ip(url: str) -> str:
    try:
        return requests.get(url).text.strip()
    except:  # Something went wrong!
        return None


def do_update(
    domain: str,
    host: str,
    token: str,
    ipv6: bool,
    ipv4_url: str,
    ipv6_url: str,
) -> None:
    client = LinodeClient(token)

    # Get public IPs
    ipv4_ip = get_ip(ipv4_url)
    click.echo(f"IPv4 IP: {ipv4_ip}")
    if ipv6:
        ipv6_ip = get_ip(ipv6_url)
        click.echo(f"IPv6 IP: {ipv6_ip}")

    # Get domain information from account
    domains = client.domains(Domain.domain == domain)
    if domains.total_items == 0:
        click.echo(f"Failed to find '{domain}' on account", err=True)
        exit(1)
    try:
        # Get the domain and ensure there is one (and only one) result
        domain = domains.only()
    except ValueError:
        click.echo(
            f"Unexpectedly found multiple domain entries for '{domain}' on account",
            err=True,
        )
        exit(2)

    # Get records in domain specific to our host
    records = [
        DomainRecord(client, id=r.id, parent_id=domain.id)
        for r in domain.records
        if (r.type == "A" or r.type == "AAAA") and r.name == host
    ]

    # Create/Update IPv4 record
    if ipv4_ip:
        ipv4_record = next(
            iter(r for r in records if r.type == "A" and r.name == host), None
        )
        if ipv4_record:  # Found
            if ipv4_record.target != ipv4_ip:
                old_ip = ipv4_record.target
                ipv4_record.target = ipv4_ip
                ipv4_record.save()
                click.echo(f"Updated A record '{host}' from '{old_ip}' to '{ipv4_ip}'")
            else:
                click.echo(f"A record '{host}' already set to '{ipv4_ip}'")
        else:  # Not found
            ipv4_record = domain.record_create("A", name=host, target=ipv4_ip)
            click.echo(f"Created new A record '{host}' with '{ipv4_ip}'")
    else:
        click.echo("Skipped A record -- no public IPv4 address found", err=True)

    # Create/Update IPv6 record
    if ipv6 and ipv6_ip:
        ipv6_record = next(
            iter(r for r in records if r.type == "AAAA" and r.name == host), None
        )
        if ipv6_record:  # Found
            if ipv6_record.target != ipv6_ip:
                old_ip = ipv6_record.target
                ipv6_record.target = ipv6_ip
                ipv6_record.save()
                click.echo(
                    f"Updated AAAA record '{host}' from '{old_ip}' to '{ipv6_ip}'"
                )
            else:
                click.echo(f"AAAA record '{host}' already set to '{ipv6_ip}'")
        else:  # Not found
            ipv6_record = domain.record_create("A", name=host, target=ipv6_ip)
            click.echo(f"Created new AAAA record '{host}' with '{ipv6_ip}'")
    elif ipv6 and not ipv6_ip:
        click.echo("Skipped AAAA record -- no public IPv6 address found", err=True)


@click.command(context_settings={"show_default": True})
@click.version_option(
    version=__version__,
    message=(
        f"%(prog)s, %(version)s (compiled: {'yes' if COMPILED else 'no'})\n"
        f"Python ({platform.python_implementation()}) {platform.python_version()}"
    ),
)
@click.option(
    "-d",
    "--domain",
    envvar="DOMAIN",
    type=str,
    required=True,
    help="Domain name as listed in your Linode Account (eg: example.com).",
)
@click.option(
    "-h",
    "--host",
    envvar="HOST",
    type=str,
    required=True,
    help="Host to create/update within the specified Domain (eg: mylab).",
)
@click.option(
    "-t",
    "--token",
    envvar="TOKEN",
    type=str,
    required=True,
    help="Linode API token",
)
@click.option(
    "-i",
    "--interval",
    envvar="INTERVAL",
    type=int,
    default=0,
    help="Interval to recheck IP and update Records at (in minutes).",
)
@click.option(
    "-6",
    "--ipv6",
    envvar="IPV6",
    type=bool,
    is_flag=True,
    default=False,
    help="Also grab public IPv6 address and create/update AAAA record.",
)
@click.option(
    "--ipv4-url",
    envvar="IPV4_URL",
    type=str,
    default="https://ipv4.icanhazip.com",
    help="URL to use for getting public IPv4 address.",
)
@click.option(
    "--ipv6-url",
    envvar="IPV6_URL",
    type=str,
    default="https://ipv6.icanhazip.com",
    help="URL to use for getting public IPv6 address.",
)
@click.pass_context
def main(
    ctx: click.Context,
    domain: str,
    host: str,
    token: str,
    interval: int,
    ipv6: bool,
    ipv4_url: str,
    ipv6_url: str,
) -> None:
    """A Python tool for dynamically updating Linode Domain Records with your current IP."""
    if interval > 0:
        while True:
            try:
                do_update(domain, host, token, ipv6, ipv4_url, ipv6_url)
            except Exception as e:
                click.echo(e)
            click.echo(f"Sleeping for {interval} min...")
            time.sleep(interval * 60)
            click.echo("-" * 80)
    else:
        try:
            do_update(domain, host, token, ipv6, ipv4_url, ipv6_url)
        except Exception as e:
            click.echo(e)


if __name__ == "__main__":
    main()
