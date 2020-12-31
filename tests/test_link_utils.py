import pytest

from bitcrawler import link_utils

def test_is_relative():
    url = "/test/1?some_param=some_val"
    assert True == link_utils.is_relative(url)

def test_not_is_relative():
    url = "http://python.org"
    assert False == link_utils.is_relative(url)

def test_get_base_url():
    url = "http://python.org/test/1?some_param=some_val"
    assert "http://python.org" == link_utils.get_base_url(url)

def test_is_same_host():
    url1 = "http://python.org/test/1?some_param=some_val"
    url2 = "http://python.org/search/123"
    assert link_utils.is_same_host(url1, url2)

def test_not_is_same_host():
    url1 = "http://python.org/test/1?some_param=some_val"
    url2 = "http://pandas.org/search/123"
    assert not link_utils.is_same_host(url1, url2)
