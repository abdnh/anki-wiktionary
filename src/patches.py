from .consts import consts
from .vendor import certifi


def patch_certifi() -> None:
    """
    Patch certifi to use the correct path to the CA certificate.
    This works around Anki's (unused) patch of it no longer working on macOS.
    """

    def where() -> str:
        return str(consts.dir / "vendor" / "certifi" / "cacert.pem")

    certifi.where = where
