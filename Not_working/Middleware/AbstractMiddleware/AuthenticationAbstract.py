from abc import ABC, abstractmethod 

class Authentication(ABC):
    
    @abstractmethod
    def authenticate(self, args):
        pass
    