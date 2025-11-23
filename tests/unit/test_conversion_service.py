import pytest
from src.services.conversion_service import ConversionService
from src.models.triple import Triple

def test_convert_likes():
    service = ConversionService()
    triple = service.convert("I like science fiction")
    assert triple.predicate == ":likes"
    assert triple.object == ":ScienceFiction"

def test_convert_wrote():
    service = ConversionService()
    triple = service.convert("Asimov wrote Foundation")
    assert triple.predicate == ":wrote"
    assert triple.object == ":Foundation"

def test_convert_default():
    service = ConversionService()
    triple = service.convert("Random text")
    assert triple.predicate == ":default_predicate"

def test_convert_empty_raises():
    service = ConversionService()
    with pytest.raises(ValueError):
        service.convert("")
