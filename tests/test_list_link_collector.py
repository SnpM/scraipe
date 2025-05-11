import pytest
from scraipe.classes import ILinkCollector
from scraipe.defaults.list_link_collector import ListTargeter

# filepath: scraipe/test_classes.py

# Mock subclass for ITargeter
class MockTargeter(ILinkCollector):
    pass

def test_initialization():
    links = ["http://example.com/1", "http://example.com/2"]
    targeter = ListTargeter(links)
    assert targeter.links == links

def test_collect_links():
    links = ["http://example.com/1", "http://example.com/2"]
    targeter = ListTargeter(links)
    assert list(targeter.collect_links()) == links
    
def test_iterable():
    links = ["http://example.com/1", "http://example.com/2"]
    targeter = ListTargeter(links)
    assert list(iter(targeter)) == links