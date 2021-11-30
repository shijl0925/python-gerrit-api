#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel


class GerritAccountGPGKey(BaseModel):
    def __init__(self, **kwargs):
        super(GerritAccountGPGKey, self).__init__(**kwargs)

    def delete(self):
        """
        Deletes a GPG key of a user.

        :return:
        """
        endpoint = "/accounts/%s/gpgkeys/%s" % (self.username, self.id)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))


class GerritAccountGPGKeys(object):
    def __init__(self, username, gerrit):
        self.username = username
        self.gerrit = gerrit

    def list(self):
        """
        Returns the GPG keys of an account.

        :return:
        """
        endpoint = "/accounts/%s/gpgkeys" % self.username
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        keys = []
        for key, value in result.items():
            gpg_key = value
            gpg_key.update({"id": key})
            keys.append(gpg_key)

        return GerritAccountGPGKey.parse_list(
            keys, username=self.username, gerrit=self.gerrit
        )

    def get(self, id_):
        """
        Retrieves a GPG key of a user.

        :param id_: GPG key id
        :return:
        """
        endpoint = "/accounts/%s/gpgkeys/%s" % (self.username, id_)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritAccountGPGKey.parse(
            result, username=self.username, gerrit=self.gerrit
        )

    def modify(self, input_):
        """
        Add or delete one or more GPG keys for a user.

        .. code-block:: python

            input_ = {
                "add": [
                  "-----BEGIN PGP PUBLIC KEY BLOCK-----\\nVersion: GnuPG v1\\n\\nmQENBFXUpNcBCACv4paCiyKxZ0EcKy8VaWVNkJlNebRBiyw9WxU85wPOq5Gz/3GT\\nRQwKqeY0SxVdQT8VNBw2sBe2m6eqcfZ2iKmesSlbXMe15DA7k8Bg4zEpQ0tXNG1L\\nhceZDVQ1Xk06T2sgkunaiPsXi82nwN3UWYtDXxX4is5e6xBNL48Jgz4lbqo6+8D5\\nvsVYiYMx4AwRkJyt/oA3IZAtSlY8Yd445nY14VPcnsGRwGWTLyZv9gxKHRUppVhQ\\nE3o6ePXKEVgmONnQ4CjqmkGwWZvjMF2EPtAxvQLAuFa8Hqtkq5cgfgVkv/Vrcln4\\nnQZVoMm3a3f5ODii2tQzNh6+7LL1bpqAmVEtABEBAAG0H0pvaG4gRG9lIDxqb2hu\\nLmRvZUBleGFtcGxlLmNvbT6JATgEEwECACIFAlXUpNcCGwMGCwkIBwMCBhUIAgkK\\nCwQWAgMBAh4BAheAAAoJEJNQnkuvyKSbfjoH/2OcSQOu1kJ20ndjhgY2yNChm7gd\\ntU7TEBbB0TsLeazkrrLtKvrpW5+CRe07ZAG9HOtp3DikwAyrhSxhlYgVsQDhgB8q\\nG0tYiZtQ88YyYrncCQ4hwknrcWXVW9bK3V4ZauxzPv3ADSloyR9tMURw5iHCIeL5\\nfIw/pLvA3RjPMx4Sfow/bqRCUELua39prGw5Tv8a2ZRFbj2sgP5j8lUFegyJPQ4z\\ntJhe6zZvKOzvIyxHO8llLmdrImsXRL9eqroWGs0VYqe6baQpY6xpSjbYK0J5HYcg\\nTO+/u80JI+ROTMHE6unGp5Pgh/xIz6Wd34E0lWL1eOyNfGiPLyRWn1d0yZO5AQ0E\\nVdSk1wEIALUycrH2HK9zQYdR/KJo1yJJuaextLWsYYn881yDQo/p06U5vXOZ28lG\\nAq/Xs96woVZPbgME6FyQzhf20Z2sbr+5bNo3OcEKaKX3Eo/sWwSJ7bXbGLDxMf4S\\netfY1WDC+4rTqE30JuC++nQviPRdCcZf0AEgM6TxVhYEMVYwV787YO1IH62EBICM\\nSkIONOfnusNZ4Skgjq9OzakOOpROZ4tki5cH/5oSDgdcaGPy1CFDpL9fG6er2zzk\\nsw3qCbraqZrrlgpinWcAduiao67U/dV18O6OjYzrt33fTKZ0+bXhk1h1gloC21MQ\\nya0CXlnfR/FOQhvuK0RlbR3cMfhZQscAEQEAAYkBHwQYAQIACQUCVdSk1wIbDAAK\\nCRCTUJ5Lr8ikm8+QB/4uE+AlvFQFh9W8koPdfk7CJF7wdgZZ2NDtktvLL71WuMK8\\nPOmf9f5JtcLCX4iJxGzcWogAR5ed20NgUoHUg7jn9Xm3fvP+kiqL6WqPhjazd89h\\nk06v9hPE65kp4wb0fQqDrtWfP1lFGuh77rQgISt3Y4QutDl49vXS183JAfGPxFxx\\n8FgGcfNwL2LVObvqCA0WLqeIrQVbniBPFGocE3yA/0W9BB/xtolpKfgMMsqGRMeu\\n9oIsNxB2oE61OsqjUtGsnKQi8k5CZbhJaql4S89vwS+efK0R+mo+0N55b0XxRlCS\\nfaURgAcjarQzJnG0hUps2GNO/+nM7UyyJAGfHlh5\\n=EdXO\\n-----END PGP PUBLIC KEY BLOCK-----\\n"
                ],
                "delete": [
                  "DEADBEEF",
                ]
            }
            account = client.accounts.get('kevin.shi')
            result = account.gpg_keys.modify(input_)

        :param input_: the GpgKeysInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#gpg-keys-input
        :return:
        """
        endpoint = "/accounts/%s/gpgkeys" % self.username
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def delete(self, id_):
        """
        Deletes a GPG key of a user.

        :param id_: GPG key id
        :return:
        """
        endpoint = "/accounts/%s/gpgkeys/%s" % (self.username, id_)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
