# language_model.py

from abc import ABC, abstractmethod

class LanguageModel(ABC):
    
    @abstractmethod
    def get_response(self, prompt):
        pass
