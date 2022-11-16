import platform
import requests
import os
import time
from pathlib import Path

import click

from linode_dyndns.version import version as __version__
from linode_dyndns.client import LinodeClient

COMPILED = Path(__file__).suffix in (".pyd", ".so")


def get_ipv4():
    url = os.environ.get("IPV4_URL", "https://ipv4.icanhazip.com")
    try:
        return requests.get(url).text.strip()
    except:  # Something went wrong!
        return None


def get_ipv6():
    url = os.environ.get("IPV6_URL", "https://ipv6.icanhazip.com")
    try:
        return requests.get(url).text.strip()
    except:  # IPv6 likely not supported
        return None


def do_update(domain: str, host: str, token: str, ipv6: bool) -> None:
    client = LinodeClient(token)

    # Get public IPs
    click.secho("Gathering public IPs...", fg="bright_white")
    ipv4_ip = get_ipv4()
    click.secho(f"IPv4 IP: {ipv4_ip}")
    if ipv6:
        ipv6_ip = get_ipv6()
        click.secho(f"IPv6 IP: {ipv6_ip}")

    if not ipv4_ip:
        click.secho("Failed to find public IPv4 address", fg="red", err=True)
        exit(1)

    # Get all domains on account
    click.secho("Fetching domains...", fg="bright_white")
    status, domains = client.get_domains()
    if status != 200:
        click.secho("Failed to fetch domains", fg="bright_red", err=True)
        exit(2)
    click.secho(f"Found {len(domains['data'])} domains")

    # Check if domain specified exists
    click.secho("Checking domain...", fg="bright_white")
    try:
        f_domain = next(d for d in domains["data"] if d["domain"] == domain)
    except StopIteration:
        click.secho(
            f"Failed to find '{domain}' on Linode account",
            fg="bright_red",
            bold=True,
            err=True,
        )
        exit(3)
    domain_id = f_domain["id"]
    click.secho(f"Found domain '{domain}' (id: {domain_id})")

    # Get all records in domain
    click.secho("Fetching domain records...", fg="bright_white")
    status, records = client.get_domain_records(domain_id)
    if status != 200:
        click.secho("Failed to fetch domain records", fg="bright_red", err=True)
        exit(4)
    click.secho(f"Found {len(records['data'])} records")

    # Update/Create IPv4 record
    host = "" if host == "." else host  # Treat . as "blank" root domains
    try:
        f_record4 = next(
            r for r in records["data"] if r["name"] == host and r["type"] == "A"
        )
        click.secho(
            f"Existing A record '{host}' found in '{domain}'", fg="bright_white"
        )

        status, record = client.update_domain_record(
            domain_id,
            f_record4["id"],
            target=ipv4_ip,
        )
        if status != 200:
            click.secho("Failed to update A record", fg="bright_red", err=True)
            exit(5)
        click.secho(f"Updated A record with {ipv4_ip}", fg="bright_green")
    except StopIteration:
        click.secho(
            f"Existing A record '{host}' NOT found in '{domain}'", fg="bright_white"
        )

        status, record = client.create_domain_record(
            domain_id, host, type="A", target=ipv4_ip
        )
        if status != 200:
            click.secho("Failed to create A record", fg="bright_red", err=True)
            exit(5)
        click.secho(f"Created A record with {ipv4_ip}", fg="bright_green")

    # Create/Update IPv6
    if ipv6 and ipv6_ip:
        try:
            f_record6 = next(
                r for r in records["data"] if r["name"] == host and r["type"] == "AAAA"
            )
            click.secho(
                f"Existing AAAA record '{host}' found in '{domain}'",
                fg="bright_white",
                bold=True,
            )

            status, _ = client.update_domain_record(
                domain_id, f_record6["id"], target=ipv6_ip
            )
            if status != 200:
                click.secho("Failed to update A record", fg="bright_red", err=True)
                exit(5)
            click.secho(f"Updated AAAA record with {ipv6_ip}", fg="bright_green")
        except StopIteration:
            click.secho(
                f"Existing AAAA record '{host}' NOT found in '{domain}'",
                fg="bright_white",
                bold=True,
            )

            status, _ = client.create_domain_record(
                domain_id, host, type="AAAA", target=ipv6_ip
            )
            if status != 200:
                click.secho("Failed to create AAAA record", fg="bright_red", err=True)
                exit(5)
            click.secho(f"Created AAAA record with {ipv6_ip}", fg="bright_green")
    elif ipv6 and not ipv6_ip:
        click.secho("No public IPv6 address found, skipping...", fg="bright_red")


@click.command
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
    "--ipv6",
    envvar="IPV6",
    is_flag=True,
    default=False,
    help="Also create a AAAA (if possible).",
)
@click.pass_context
def main(
    ctx: click.Context,
    domain: str,
    host: str,
    token: str,
    interval: int,
    ipv6: bool,
) -> None:
    """A Python tool for dynamically updating Linode Domain Records."""
    if interval > 0:
        while True:
            do_update(domain, host, token, ipv6)
            click.echo(f"Waiting {interval}min before next update...")
            time.sleep(interval * 60)
            click.echo("-" * 80)
    else:
        do_update(domain, host, token, ipv6)


if __name__ == "__main__":
    main()
