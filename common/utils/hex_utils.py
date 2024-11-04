def append_hex_prefix(data: str):
  if data.startswith("0x"):
    return data
  return "0x" + data