from src.models.triple import Triple

class ConversionService:
    def convert(self, text: str) -> Triple:
        try:
            # This is a mock service. In a real implementation, this would
            # use a natural language processing model to extract the triple.
            if not text:
                raise ValueError("Input text cannot be empty")
                
            if "like" in text:
                return Triple(subject=":User", predicate=":likes", object=":ScienceFiction")
            elif "wrote" in text:
                return Triple(subject=":Asimov", predicate=":wrote", object=":Foundation")
            else:
                return Triple(subject=":default_subject", predicate=":default_predicate", object=":default_object")
        except Exception as e:
            import logging
            logging.error(f"Error converting text to triple: {e}")
            raise
