"""
exceptions.py
Defines LinuxForHealth ethereum.py package exceptions.
"""

class EthereumNetworkConnectionError(Exception):
    """Raised when the client cannot ethereum to a blockchain network"""

    def __init__(self, msg):
        super(EthereumNetworkConnectionError, self).__init__(msg)