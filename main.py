#!/usr/bin/env python3

import os
import subprocess
import sys

import click


def subprocess_mkdir(path):
    print("Creating directory '{}'.".format(path))
    subprocess.run(["mkdir", "-p", path], capture_output=True)


def subprocess_cp(*, source, destination):
    print("Copying '{}' to '{}'.".format(source, destination))
    subprocess.run(["cp", source, destination], capture_output=True)


def subprocess_dnf(target, release, *args):
    print("Running DNF in '{}'.".format(target))
    result = subprocess.run(
        ["dnf", "-y", "--nogpgcheck", "--installroot", target, "--releasever", release]
        + list(args),
        stdin=os.sys.stdin,
        stdout=os.sys.stdout,
        stderr=os.sys.stderr,
    )
    if result.stderr:
        print(result.stderr.decode("utf-8"))


def subprocess_rm(path):
    print("Removing '{}'.".format(path))
    subprocess.run(["rm", "-rf", path], capture_output=True)


@click.command
@click.option("--release", required=True, help="Fedora release version.")
@click.option(
    "--target", required=True, help="Target directory. For example: /mnt/chroot"
)
@click.option(
    "--enable-repo-thirdparty-rpmfusion",
    is_flag=True,
    help="Enable RPMFusion repository.",
)
@click.option(
    "--enable-repo-thirdparty-vscode",
    is_flag=True,
    help="Enable Visual Studio Code repository.",
)
@click.option(
    "--enable-repo-thirdparty-googlechrome",
    is_flag=True,
    help="Enable Google Chrome repository.",
)
@click.option(
    "--enable-repo-thirdparty-brave", is_flag=True, help="Enable Brave repository."
)
@click.option(
    "--enable-repo-thirdparty-nordvpn", is_flag=True, help="Enable NordVPN repository."
)
@click.option(
    "--enable-repo-thirdparty-docker", is_flag=True, help="Enable Docker repository."
)
@click.option(
    "--enable-repo-copr-ltskernel515",
    is_flag=True,
    help="Enable COPR LTS kernel 5.15 repository.",
)
@click.option(
    "--enable-repo-copr-racket", is_flag=True, help="Enable Racket repository."
)
@click.option("--enable-repo-copr-golang", is_flag=True, help="Enable Go repository.")
@click.option("--enable-repo-copr-sbcl", is_flag=True, help="Enable SBCL repository.")
@click.option("--enable-repo-all", is_flag=True, help="Enable all repositories.")
def install(
    release,
    target,
    enable_repo_all,
    **kwargs,
):
    if os.path.abspath(target) != target:
        print("Target directory must be absolute.")
        sys.exit(1)

    print("Installing Fedora {} in '{}'.".format(release, target))

    repos = {
        key.replace("enable_repo_", "").replace("_", "-"): True
        if enable_repo_all
        else value
        for key, value in kwargs.items()
        if "enable_repo" in key
    }
    for name, enabled in repos.items():
        print("Enabling {} repository? {}".format(name, enabled))

    for name in [
        "fedora",
        "fedora-updates",
        "fedora-modular",
        "fedora-updates-modular",
        "fedora-cisco-openh264",
    ]:
        repos[name] = True

    if input("Continue? [y/N] ").lower().strip() != "y":
        print("Aborting.")
        sys.exit(1)

    subprocess_mkdir(os.path.join(target, "etc/yum.repos.d"))
    subprocess_mkdir(os.path.join(target, "etc/dnf"))
    subprocess_cp(
        source="dnf.conf", destination=os.path.join(target, "etc/dnf/dnf.conf")
    )

    for name, enabled in repos.items():
        source_filepath = os.path.join("repos", name + ".repo")

        if enabled and os.path.exists(source_filepath):
            subprocess_cp(
                source=source_filepath,
                destination=os.path.join(target, "etc/yum.repos.d"),
            )

    subprocess_dnf(
        target, release, "groupinstall", "Minimal Install", "base-x", "i3 desktop"
    )
    subprocess_dnf(
        target,
        release,
        "install",
        "NetworkManager",
        "NetworkManager-wifi",
        "wpa_supplicant",
        "network-manager-applet",
    )
    subprocess_dnf(
        target,
        release,
        "install",
        "kernel",
        "kernel-modules",
        "kernel-modules-extra",
        "kernel-devel",
        "kernel-devel-matches",
        "linux-firmware",
    )
    subprocess_dnf(
        target,
        release,
        "install",
        "iwlax2xx-firmware",
        "intel-gpu-firmware",
        "amd-gpu-firmware",
        "nvidia-gpu-firmware",
    )
    subprocess_dnf(
        target, release, "install", "sddm", "rofi", "arandr", "lxrandr", "autorandr"
    )
    subprocess_dnf(target, release, "install", "git", "vim", "htop", "btop", "iotop")
    subprocess_dnf(target, release, "install", "xfsprogs", "dosfstools", "btrfs-progs")
    subprocess_dnf(
        target, release, "install", "pipewire", "pipewire-pulseaudio", "wireplumber"
    )
    subprocess_dnf(target, release, "install", "fedora-gpg-keys")


if __name__ == "__main__":
    install()
