import logging
import textwrap

import pytest

from config_utils.log_utils import BufferingSMTPHandler, MessageTypeAdapter


@pytest.fixture(
    params=[
        {"subject": "cats", "predicate": "bounce amusingly"},
    ]
)
def template_vars(request):
    return request.param


@pytest.fixture
def template(template_vars):
    return textwrap.dedent(
        f"""
        <!DOCTYPE html>
        <html>
          <body>
            {"	".join([f"{n}: %({n})s" for n in template_vars])}
          </body>
        </html>
    """
    )


@pytest.fixture(params=["", "foo", "foo.bar", "foo.bar.baz"])
def logger_name(request):
    return request.param


@pytest.fixture(
    params=[
        {"pet": "chinchilla", "telescope": "refracting"},
    ]
)
def extras(request):
    return request.param


@pytest.fixture
def root_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.setLevel("DEBUG")
    return logger


@pytest.fixture
def smtp_logger_adapter(extras, root_logger, smtp_handler):
    root_logger.addHandler(smtp_handler)
    adapter = MessageTypeAdapter(root_logger, "email", **extras)
    yield adapter
    root_logger.handlers.clear()


@pytest.fixture(
    params=["testy@irate.net", "testudo@drytortugas.com", "foobar@withgoogle.com"]
)
def fromAddr(request):
    return request.param


@pytest.fixture(
    params=[
        ["one@first.com", "two@second.com"],
    ]
)
def toAddrs(request):
    return request.param


@pytest.fixture(
    params=[
        ["one@first.com", "two@second.com"],
        ["ordinal@surreal.com", "cardinal@continuum.gov"],
        ["cantor@diagonal.org", "cohen@forcing.net"],
    ]
)
def ccAddrs(request):
    return request.param


@pytest.fixture(
    params=[
        ["one@first.com", "two@second.com"],
    ]
)
def bccAddrs(request):
    return request.param


@pytest.fixture(params=["Test", "Lost pigeon", "funny cat picz"])
def subject(request):
    return request.param


@pytest.fixture
def datefmt():
    return "%Y-%m-%d %H:%M:%S"


@pytest.fixture
def smtp_handler(
    template, smtpd, datefmt, toAddrs, fromAddr, ccAddrs, bccAddrs, subject
):
    return BufferingSMTPHandler(
        1,
        template,
        "html",
        smtpd.hostname,
        smtpd.port,
        datefmt=datefmt,
        toAddrs=toAddrs,
        fromAddr=fromAddr,
        ccAddrs=ccAddrs,
        bccAddrs=bccAddrs,
        subject=subject,
    )


def test_logger_setup(smtpd, template_vars, template, smtp_logger_adapter, subject):
    """
    Use the pytest-smtpd fixture to inject a mock SMTP server
    Requires `pip install pytest-smtpd`
    """
    smtp_logger_adapter.info("Hi there", email=template_vars)
    assert len(smtpd.messages) == 1