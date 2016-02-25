#
# Copyright (C) 2016 Bert Vermeulen <bert@biot.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import logging
import select
import socket


DEFAULT_DB = 'OpenSwitch'
OVSDB_TIMEOUT_MS = 1000


class Ovsdb:
    def __init__(self, server):
        self.server = server
        self.seq = 0

    def connect(self):
        parts = self.server.split(':')
        if len(parts) < 2:
            raise Exception("Invalid server")
        if parts[0] == 'tcp':
            if len(parts) != 3 or not parts[2].isdigit():
                raise Exception("Invalid server")
            ipv4addr, port = parts[1:]
            address = (ipv4addr, int(port))
            logging.info("Connecting to %s port %d" % address)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif parts[0] == 'unix':
            if len(parts) != 2:
                raise Exception("Invalid server")
            address = parts[1]
            logging.info("Connecting to %s" % address)
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            # TODO: ssl connection method
            raise Exception("unsupported connection method")

        self.socket.connect(address)
        logging.info("Connected.")

    def close(self):
        self.socket.close()
        logging.info("Closed connection.")

    def send(self, msg):
        logging.info("Sending %s" % msg)
        self.socket.send(json.dumps(msg))

    def receive(self):
        results = {}
        p = select.poll()
        p.register(self.socket, select.POLLIN)
        data = ''
        while True:
            fdlist = p.poll(OVSDB_TIMEOUT_MS)
            if not fdlist:
                # Timeout.
                break
            if fdlist[0][1] & select.POLLERR:
                raise Exception("poll error")
            chunk = self.socket.recv(4096)
            logging.info("Received %d bytes." % len(chunk))
            logging.info(chunk)
            if len(chunk) == 0:
                raise Exception
            data += chunk
            try:
                results = json.loads(data)
                # If we made it here, we have a valid JSON block.
                break
            except Exception:
                # Didn't parse, incomplete.
                pass
        return results

    def _select(self, table, columns=None, conditions=[]):
        select = {
            "op": "select",
            "table": table,
            "where": conditions,
        }
        if columns:
            select["columns"] = columns
        return select

    def _insert(self, table, row):
        insert = {
            "op": "insert",
            "table": table,
            "row": row,
        }
        return insert

    def _update(self, table, row, conditions=[]):
        update = {
            "op": "insert",
            "table": table,
            "where": conditions,
            "row": row,
        }
        return update

    def _mutate(self, table, mutations, conditions=[]):
        mutate = {
            "op": "mutate",
            "table": table,
            "where": conditions,
            "mutations": mutations,
        }
        return mutate

    def _transact(self, database, seq, operations):
        transact = {
            "method": "transact",
            "params": [database, operations],
            "id": seq
        }
        return transact

    def transact(self, transaction, database=DEFAULT_DB):
        self.seq += 1
        tmp = self._transact(database, self.seq, transaction)
        self.send(tmp)
        while True:
            response = self.receive()
            if response.get('id') == self.seq:
                break
        if response['error'] is not None:
            raise Exception(response['error'])
        elif 'error' in response['result'][0]:
            raise Exception(response['result'][0])
        return response['result'][0]

    def query(self, table, columns=None, conditions=[], database=DEFAULT_DB):
        self.seq += 1
        select = self._select(table, columns, conditions)
        transact = self._transact(database, self.seq, select)
        self.send(transact)
        while True:
            response = self.receive()
            if response.get('id') == self.seq:
                break
        if response['error'] is not None:
            raise Exception(response['error'])
        elif 'error' in response['result'][0]:
            raise Exception(response['result'][0])
        return response['result'][0]['rows']


    def get(self, table, columns=None, conditions=[], database=DEFAULT_DB):
        self.connect()
        response = self.query(table=table, columns=columns,
                                conditions=conditions, database=database)
        self.close()

        return response


    def get_map(self, table, column, conditions=[]):
        data = self.get(table, [column], conditions=conditions)[0][column][1]
        results = {}
        for key, value in data:
            results[key] = value

        return results


    def insert(self, table, row, database=DEFAULT_DB):
        self.connect()
        tr = self._insert(table, row)
        response = self.transact(tr, database=database)
        self.close()

        return response


    def update(self, table, row, conditions=[], database=DEFAULT_DB):
        self.connect()
        tr = self._update(table, row, conditions)
        response = self.transact(tr, database=database)
        self.close()

        return response


    def mutate_map(self, table, mutations, conditions=[]):
        self.connect()
        tr = self._mutate(table, mutations, conditions)
        response = self.transact(tr, database=DEFAULT_DB)
        self.close()

        return response


    def map_set_key(self, table, column, key, value, conditions=[]):
        self.connect()
        mutations = [
            [column, 'delete', ['set', [key]]],
            [column, 'insert', ['map', [[key, value]]]],
        ]
        tr = self._mutate(table, mutations, conditions)
        response = self.transact(tr, database=DEFAULT_DB)
        self.close()

        return response


    def map_delete_key(self, table, column, key, conditions=[]):
        self.connect()
        mutations = [
            [column, 'delete', ['set', [key]]],
        ]
        tr = self._mutate(table, mutations, conditions)
        response = self.transact(tr, database=DEFAULT_DB)
        self.close()

        return response
