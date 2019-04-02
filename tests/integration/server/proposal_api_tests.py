# Copyright 2018 Contributors to Hyperledger Sawtooth
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
# -----------------------------------------------------------------------------
"""Integration tests for propasal APIs"""
import requests
import rethinkdb as r
from rbac.providers.common.db_queries import connect_to_db
from rbac.common.logs import get_default_logger


LOGGER = get_default_logger(__name__)


def test_compile_proposal_resource():
    """Testing compile proposal resource"""
    with requests.Session() as session:
        user_payload = {
            "name": "Kiran",
            "username": "Kumar",
            "password": "12345",
            "email": "kiran@biz.co",
        }
        user_response = session.post(
            "http://rbac-server:8000/api/users", json=user_payload
        )
        manager = user_response.json()["data"]["user"]["id"]
        temp_id = user_response.json()["data"]["user"]["id"]
        user_payload = {
            "name": "NickCriss",
            "username": "crissnick",
            "password": "12345",
            "email": "criss@biz.co",
        }
        user_response = session.post(
            "http://rbac-server:8000/api/users", json=user_payload
        )
        roleowner = user_response.json()["data"]["user"]["id"]
        conn = connect_to_db()
        r.table("users").filter({"user_id": roleowner}).update(
            {"manager_id": temp_id}
        ).run(conn)
        conn.close()
        conn = connect_to_db()
        r.table("users").filter({"user_id": manager}).update(
            {"remote_id": temp_id}
        ).run(conn)
        conn.close()
        role_resource = {
            "name": "Test role for update",
            "owners": roleowner,
            "administrators": roleowner,
        }
        response = session.post("http://rbac-server:8000/api/roles", json=role_resource)
        user_payload = {
            "name": "henryki",
            "username": "henryidop",
            "password": "12345akl",
            "email": "henrysmal@biz.co",
        }
        user_response = session.post(
            "http://rbac-server:8000/api/users", json=user_payload
        )
        user_id = user_response.json()["data"]["user"]["id"]
        role_payload = {"id": user_id, "reason": "add the test member"}
        role_response = session.post(
            "http://rbac-server:8000/api/roles/"
            + response.json()["data"]["id"]
            + "/members",
            json=role_payload,
        )
        proposal_response = session.get(
            "http://rbac-server:8000/api/proposals/"
            + role_response.json()["proposal_id"]
        )
        assert roleowner in proposal_response.json()["data"]["approvers"]
        assert manager in proposal_response.json()["data"]["approvers"]
