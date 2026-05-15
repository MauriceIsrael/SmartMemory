import mcp.server
from mcp.server import Server

s = Server("test")
print(f"Attributes: {dir(s)}")
