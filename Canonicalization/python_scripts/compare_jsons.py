def compare_jsons(first, second):
	""" 
	Returns True if both JSON files match in their dates published and city.
	Else, returns false.
	"""
	first_df = pd.read_json(first)
	second_df = pd.read_json(second)
	first_date, second_date = first_df["date_published"][0], second_df["date_published"][0]
	first_city, second_city = first_df["city"][0], second_df["city"][0]
	if first_date == second_date and first_city == second_city:
		return True
	else:
		return False
