import os
import subprocess

import pytest

# Treat all tests as coroutines
pytestmark = pytest.mark.asyncio

juju_repository = os.getenv("JUJU_REPOSITORY", ".").rstrip("/")
series = [
    "xenial",
    "bionic",
    pytest.param("disco", marks=pytest.mark.xfail(reason="canary")),
]
sources = [
    ("local", "{}/builds/samba-server".format(juju_repository)),
    ('jujucharms', 'cs:~pirate-charmers/samba-server'),
]


# Custom fixtures
@pytest.fixture(params=series)
def series(request):
    return request.param


@pytest.fixture(params=sources, ids=[s[0] for s in sources])
def source(request):
    return request.param


@pytest.fixture
async def app(model, series, source):
    app_name = "samba-server-{}-{}".format(series, source[0])
    return await model._wait_for_new("application", app_name)


@pytest.mark.deploy
@pytest.mark.timeout(60)
async def test_samba_deploy(model, series, source, request):
    # Starts a deploy for each series
    # Using subprocess b/c libjuju fails with JAAS
    # https://github.com/juju/python-libjuju/issues/221
    application_name = "samba-server-{}-{}".format(series, source[0])
    cmd = [
        "juju",
        "deploy",
        source[1],
        "-m",
        model.info.name,
        "--series",
        series,
        application_name,
    ]
    if request.node.get_closest_marker("xfail"):
        # If series is 'xfail' force install to allow testing against versions not in
        # metadata.yaml
        cmd.append("--force")
    subprocess.check_call(cmd)


@pytest.mark.deploy
@pytest.mark.timeout(420)
async def test_charm_upgrade(model, app):
    if app.name.endswith("local"):
        pytest.skip("No need to upgrade the local deploy")
    unit = app.units[0]
    await model.block_until(lambda: unit.agent_status == "idle")
    subprocess.check_call(
        [
            "juju",
            "upgrade-charm",
            "--switch={}".format(sources[0][1]),
            "-m",
            model.info.name,
            app.name,
        ]
    )
    await model.block_until(lambda: unit.agent_status == "executing")


# Tests
@pytest.mark.timeout(420)
async def test_samba_status(model, app):
    # Verifies status for all deployed series of the charm
    await model.block_until(lambda: app.status == "active")
    unit = app.units[0]
    await model.block_until(lambda: unit.agent_status == "idle")
