import json

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

from math import log10, floor

def round_to_sig(x, sig=2):
    return round(x, sig-1-int(floor(log10(abs(x)))))


