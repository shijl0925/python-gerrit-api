#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import json
import inspect
import logging
from functools import wraps


def strip_trailing_slash(url):
    """
    remove url's trailing slash
    :param url: url
    :return:
    """
    while url.endswith("/"):
        url = url[:-1]
    return url


def decode_response(response):
    """Strip off Gerrit's magic prefix and decode a response.
    :returns:
        Decoded JSON content as a dict, or raw text if content could not be
        decoded as JSON.
    :raises:
        requests.HTTPError if the response contains an HTTP error status code.
    """
    magic_json_prefix = ")]}'\n"
    content_type = response.headers.get("content-type", "")

    content = response.content.strip()
    if response.encoding:
        content = content.decode(response.encoding)
    if not content:
        return content
    if content_type.split(";")[0] != "application/json":
        return content
    if content.startswith(magic_json_prefix):
        index = len(magic_json_prefix)
        content = content[index:]
    try:
        return json.loads(content)
    except ValueError:
        raise ValueError(f"Invalid json content: {content}")


def params_creator(tuples, pattern_types, pattern_dispatcher):
    p, v = None, None
    if pattern_dispatcher is not None and pattern_dispatcher:
        for item in pattern_types:
            if item in pattern_dispatcher:
                p, v = pattern_types[item], pattern_dispatcher[item]
                break
        else:
            k = list(pattern_types.keys())
            raise ValueError(
                "Pattern types can be either " + ", ".join(k[:-1]) + " or " + k[-1]
            )

    params = {k: v for k, v in tuples + ((p, v),) if v is not None}

    return params


def check(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(fn)
        params = sig.parameters
        argspec = list(params.keys())

        # check args and kwargs type
        for i, p in enumerate(args):
            arg_type = fn.__annotations__.get(argspec[i], None)
            if arg_type and not isinstance(p, arg_type):
                raise TypeError(
                    f"{argspec[i]} should be {arg_type.__name__}, not {type(p).__name__}"
                )
        for k, v in kwargs.items():
            kwarg_type = fn.__annotations__.get(k, None)
            if kwarg_type and not isinstance(v, kwarg_type):
                raise TypeError(
                    f"{k} should be {kwarg_type.__name__}, not {type(v).__name__}"
                )

        result = fn(*args, **kwargs)

        # check return type
        return_type = fn.__annotations__.get("return", None)
        if return_type and not isinstance(result, return_type):
            raise TypeError(
                f"{fn.__name__} should return {return_type.__name__}, not {type(result).__name__}"
            )

        return result

    return wrapper


# create logger
logger = logging.getLogger("gerrit")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.root.setLevel(logging.NOTSET)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)