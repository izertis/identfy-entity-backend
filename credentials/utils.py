def get_first_matching_element(list, candidate):
  result = None
  for value in candidate:
    if value in list:
      result = value
      break
  return result
