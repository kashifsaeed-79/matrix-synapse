# Copyright 2015, 2016 OpenMarket Ltd
# Copyright 2017 Vector Creations Ltd
# Copyright 2018 New Vector Ltd
# Copyright 2020 The Matrix.org Foundation C.I.C.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools
import logging
from typing import Set

logger = logging.getLogger(__name__)


# REQUIREMENTS is a simple list of requirement specifiers[1], and must be
# installed. It is passed to setup() as install_requires in setup.py.
#
# CONDITIONAL_REQUIREMENTS is the optional dependencies, represented as a dict
# of lists. The dict key is the optional dependency name and can be passed to
# pip when installing. The list is a series of requirement specifiers[1] to be
# installed when that optional dependency requirement is specified. It is passed
# to setup() as extras_require in setup.py
#
# Note that these both represent runtime dependencies (and the versions
# installed are checked at runtime).
#
# Also note that we replicate these constraints in the Synapse Dockerfile while
# pre-installing dependencies. If these constraints are updated here, the same
# change should be made in the Dockerfile.
#
# [1] https://pip.pypa.io/en/stable/reference/pip_install/#requirement-specifiers.

REQUIREMENTS = [
    # we use the TYPE_CHECKER.redefine method added in jsonschema 3.0.0
    "jsonschema>=3.0.0",
    # frozendict 2.1.2 is broken on Debian 10: https://github.com/Marco-Sulla/python-frozendict/issues/41
    "frozendict>=1,!=2.1.2",
    "unpaddedbase64>=1.1.0",
    "canonicaljson>=1.4.0",
    # we use the type definitions added in signedjson 1.1.
    "signedjson>=1.1.0,<=1.1.1",
    "pynacl>=1.2.1",
    "idna>=2.5",
    # validating SSL certs for IP addresses requires service_identity 18.1.
    "service_identity>=18.1.0",
    # Twisted 18.9 introduces some logger improvements that the structured
    # logger utilises
    "Twisted>=18.9.0",
    "treq>=15.1",
    # Twisted has required pyopenssl 16.0 since about Twisted 16.6.
    "pyopenssl>=16.0.0",
    "pyyaml>=3.11",
    "pyasn1>=0.1.9",
    "pyasn1-modules>=0.0.7",
    "bcrypt>=3.1.0",
    "pillow>=5.4.0",
    "sortedcontainers>=1.4.4",
    "pymacaroons>=0.13.0",
    "msgpack>=0.5.2",
    "phonenumbers>=8.2.0",
    # we use GaugeHistogramMetric, which was added in prom-client 0.4.0.
    "prometheus_client>=0.4.0",
    # we use `order`, which arrived in attrs 19.2.0.
    # Note: 21.1.0 broke `/sync`, see #9936
    "attrs>=19.2.0,!=21.1.0",
    "netaddr>=0.7.18",
    # Jinja 2.x is incompatible with MarkupSafe>=2.1. To ensure that admins do not
    # end up with a broken installation, with recent MarkupSafe but old Jinja, we
    # add a lower bound to the Jinja2 dependency.
    "Jinja2>=3.0",
    "bleach>=1.4.3",
    # We use `ParamSpec`, which was added in `typing-extensions` 3.10.0.0.
    "typing-extensions>=3.10.0",
    # We enforce that we have a `cryptography` version that bundles an `openssl`
    # with the latest security patches.
    "cryptography>=3.4.7",
    # ijson 3.1.4 fixes a bug with "." in property names
    "ijson>=3.1.4",
    "matrix-common~=1.1.0",
    # We need packaging.requirements.Requirement, added in 16.1.
    "packaging>=16.1",
    # EXPERIMENTAL: Faster JSON deserialisation for replication messages
    "orjson>=3.6.7",
]

CONDITIONAL_REQUIREMENTS = {
    "matrix-synapse-ldap3": ["matrix-synapse-ldap3>=0.1"],
    "postgres": [
        # we use execute_values with the fetch param, which arrived in psycopg 2.8.
        "psycopg2>=2.8 ; platform_python_implementation != 'PyPy'",
        "psycopg2cffi>=2.8 ; platform_python_implementation == 'PyPy'",
        "psycopg2cffi-compat==1.1 ; platform_python_implementation == 'PyPy'",
    ],
    "saml2": [
        "pysaml2>=4.5.0",
    ],
    "oidc": ["authlib>=0.14.0"],
    # systemd-python is necessary for logging to the systemd journal via
    # `systemd.journal.JournalHandler`, as is documented in
    # `contrib/systemd/log_config.yaml`.
    "systemd": ["systemd-python>=231"],
    "url_preview": ["lxml>=4.2.0"],
    "sentry": ["sentry-sdk>=0.7.2"],
    "opentracing": ["jaeger-client>=4.0.0", "opentracing>=2.2.0"],
    "jwt": ["pyjwt>=1.6.4"],
    # hiredis is not a *strict* dependency, but it makes things much faster.
    # (if it is not installed, we fall back to slow code.)
    "redis": ["txredisapi>=1.4.7", "hiredis"],
    # Required to use experimental `caches.track_memory_usage` config option.
    "cache_memory": ["pympler"],
}

ALL_OPTIONAL_REQUIREMENTS: Set[str] = set()

for name, optional_deps in CONDITIONAL_REQUIREMENTS.items():
    # Exclude systemd as it's a system-based requirement.
    # Exclude lint as it's a dev-based requirement.
    if name not in ["systemd"]:
        ALL_OPTIONAL_REQUIREMENTS = set(optional_deps) | ALL_OPTIONAL_REQUIREMENTS


# ensure there are no double-quote characters in any of the deps (otherwise the
# 'pip install' incantation in DependencyException will break)
for dep in itertools.chain(
    REQUIREMENTS,
    *CONDITIONAL_REQUIREMENTS.values(),
):
    if '"' in dep:
        raise Exception(
            "Dependency `%s` contains double-quote; use single-quotes instead" % (dep,)
        )


def list_requirements():
    return list(set(REQUIREMENTS) | ALL_OPTIONAL_REQUIREMENTS)


if __name__ == "__main__":
    import sys

    sys.stdout.writelines(req + "\n" for req in list_requirements())
