from enum import Enum

class DataRepositoryType(str, Enum):
    Vector = "vector",
    HelpSapCom = "help.sap.com",
    RemoteDg = "remote:dg",

