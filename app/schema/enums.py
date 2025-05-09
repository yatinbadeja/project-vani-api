from enum import Enum

class UserTypeEnum(str,Enum):
    ADMIN = "admin"
    User = "user"
    
class UserRole(str,Enum):
    STOCKIST = "Stockist"
    CHEMIST = "Chemist"

class StockMovementTypeEnum(str, Enum):
    IN = "IN"
    OUT = "OUT"
    RETURN= "RETURN"