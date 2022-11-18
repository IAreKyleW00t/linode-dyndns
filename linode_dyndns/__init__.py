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
    click.secho("Gathering public IPs...", fg="bright_white")
    ipv4_ip = get_ip(ipv4_url)
    click.secho(f"IPv4 IP: {ipv4_ip}")
    if ipv6:
        ipv6_ip = get_ip(ipv6_url)
        click.secho(f"IPv6 IP: {ipv6_ip}")

    if not ipv4_ip:
        click.secho("Failed to find public IPv4 address", fg="red", err=True)
        exit(1)

    # Get domain information from account
    click.secho(f"Fetching domain from account...", fg="bright_white")
    domains = client.domains(Domain.domain == domain)
    if domains.total_items == 0:
        click.secho(
            f"Failed to find '{domain}' on account",
            fg="bright_red",
            bold=True,
            err=True,
        )
        exit(2)
    try:
        # Get the domain and ensure there is one (and only one) result
        domain = domains.only()
    except ValueError:
        click.secho(
            f"Unexpectedly found multiple domain entries for '{domain}' on account",
            fg="bright_red",
            bold=True,
            err=True,
        )
        exit(2)
    click.secho(f"Found domain '{domain.domain}'")

    # Get all records in domain
    records = [
        DomainRecord(client, id=r.id, parent_id=domain.id) for r in domain.records
    ]

    # Create/Update IPv4 record
    ipv4_record = next(
        iter(r for r in records if r.type == "A" and r.name == host), None
    )
    if ipv4_record:  # Found
        if ipv4_record.target != ipv4_ip:
            old_ip = ipv4_record.target
            ipv4_record.target = ipv4_ip
            ipv4_record.save()
            click.secho(
                f"Updated A record '{host}' from '{old_ip}' to '{ipv4_ip}'",
                fg="bright_green",
            )
        else:
            click.secho(
                f"A record '{host}' already set to '{ipv4_ip}'", fg="bright_green"
            )
    else:  # Not found
        ipv4_record = domain.record_create("A", name=host, target=ipv4_ip)
        click.secho(
            f"Created new A record '{host}' with '{ipv4_ip}'", fg="bright_green"
        )

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
                click.secho(
                    f"Updated AAAA record '{host}' from '{old_ip}' to '{ipv6_ip}'",
                    fg="bright_green",
                )
            else:
                click.secho(
                    f"AAAA record '{host}' already set to '{ipv6_ip}'",
                    fg="bright_green",
                )
        else:  # Not found
            ipv6_record = domain.record_create("A", name=host, target=ipv6_ip)
            click.secho(
                f"Created new AAAA record '{host}' with '{ipv6_ip}'",
                fg="bright_green",
            )
    elif ipv6 and not ipv6_ip:
        click.secho(
            "Skipped AAAA record -- no public IPv6 address found", fg="bright_red"
        )


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
    required=False,
    help="Interval to recheck IP and update Records at (in minutes).",
)
@click.option(
    "-6",
    "--ipv6",
    envvar="IPV6",
    is_flag=True,
    default=False,
    help="Also create a AAAA record (if possible).",
)
@click.option(
    "--ipv4-url",
    envvar="IPV4_URL",
    type=str,
    required=False,
    default="https://ipv4.icanhazip.com",
    help="URL to use for getting public IPv4 address",
)
@click.option(
    "--ipv6-url",
    envvar="IPV6_URL",
    type=str,
    required=False,
    default="https://ipv6.icanhazip.com",
    help="URL to use for getting public IPv6 address",
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
            do_update(domain, host, token, ipv6, ipv4_url, ipv6_url)
            click.echo(f"Waiting {interval}min before next update...")
            time.sleep(interval * 60)
            click.echo("-" * 80)
    else:
        do_update(domain, host, token, ipv6, ipv4_url, ipv6_url)


if __name__ == "__main__":
    main()
