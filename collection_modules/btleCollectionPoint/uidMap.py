class UIDMap(object):
	""" Class to hold a dict of uid to object pairs. """
	def __init__(self):
		# Build dict of uid -> string pairs. Could be changed to map objects.
		self.map = {
			'00000000000000000000000000000001': 'Education',
			'00000000000000000000000000000002': 'Media-and-Entertainment',
			'00000000000000000000000000000003': 'FSI',
			'00000000000000000000000000000004': 'Retail',
			'00000000000000000000000000000005': 'Government',
			'00000000000000000000000000000006': 'Healthcare',
			'00000000000000000000000000000007': 'High-Tech',
			'00000000000000000000000000000008': 'Manufacturing',
			'00000000000000000000000000000009': 'Telco',
			'00000000000000000000000000000010': 'Travel-and-Hospitality',
			'A2FA7357C8CD4B9598FD9D091CE43337': 'Government' 
		}

	def get(self, uid):
		try:
			return self.map[uid]
		except Exception as e:
			return ''