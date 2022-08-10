import gnupg
import os
import pytest

from ansible_sign.signing import *

__author__ = "Rick Elrod"
__copyright__ = "(c) 2022 Red Hat, Inc."
__license__ = "MIT"


FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fixtures",
)


@pytest.mark.parametrize(
    "directory, expected",
    [
        ("hao-signed", True),
        ("hao-signed-invalid", False),
    ],
)
def test_gpg_simple_verify(tmp_path, directory, expected):
    gpg = gnupg.GPG(gnupghome=tmp_path)
    pubkey = open(os.path.join(FIXTURES_DIR, "gpgkeys", "hao_pubkey.txt"), "r").read()
    gpg.import_keys(pubkey)

    manifest_path = os.path.join(
        FIXTURES_DIR, "gpg", directory, ".ansible-sign", "sha256sum.txt"
    )
    signature_path = os.path.join(
        FIXTURES_DIR, "gpg", directory, ".ansible-sign", "sha256sum.txt.sig"
    )

    verifier = GPGVerifier(
        manifest_path=manifest_path,
        detached_signature_path=signature_path,
        gpg_home=tmp_path,
    )

    result = verifier.verify()
    assert result.success is expected


def test_gpg_simple_sign(
    gpg_home_with_secret_key,
    unsigned_project_with_checksum_manifest,
):
    out = (
        unsigned_project_with_checksum_manifest / ".ansible-sign" / "sha256sum.txt.asc"
    )
    manifest_path = (
        unsigned_project_with_checksum_manifest / ".ansible-sign" / "sha256sum.txt"
    )
    signer = GPGSigner(
        manifest_path=manifest_path,
        output_path=out,
        passphrase="doYouEvenPassphrase",
        gpg_home=gpg_home_with_secret_key,
    )
    result = signer.sign()
    assert result.success is True
    assert os.path.exists(out)


def test_gpg_sign_verify_end_to_end(signed_project_and_gpg):
    project_root = signed_project_and_gpg[0]
    gpg_home = signed_project_and_gpg[1]

    manifest_path = project_root / ".ansible-sign" / "sha256sum.txt"
    signature_path = project_root / ".ansible-sign" / "sha256sum.txt.asc"

    verifier = GPGVerifier(
        manifest_path=manifest_path,
        detached_signature_path=signature_path,
        gpg_home=gpg_home,
    )
    result = verifier.verify()
    assert result.success is True
