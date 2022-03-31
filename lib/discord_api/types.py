import json

__all__ = [
    "GatewayPayload"
]

class GatewayPayload:
    def __init__(self, op, d, s, t):
        self.op = op
        self.d = d
        self.s = s
        self.t = t

    @classmethod
    def from_parsed_json(cls, parsed_json):
        op = parsed_json["op"] if "op" in parsed_json else None
        d =  parsed_json["d"]  if "d"  in parsed_json else None
        s =  parsed_json["s"]  if "s"  in parsed_json else None
        t =  parsed_json["t"]  if "t"  in parsed_json else None

        return cls(op, d, s, t)

    @classmethod
    def from_json_str(cls, json_str):
        parsed_json = json.loads(json_str)

        return cls.from_parsed_json(parsed_json)

    def to_json(self):
        json_dict = {}

        if self.op is not None:
            json_dict["op"] = self.op

        if self.d is not None:
            json_dict["d"] = self.d

        if self.s is not None:
            json_dict["s"] = self.s

        if self.t is not None:
            json_dict["t"] = self.t

        return json.dumps(json_dict)

    def __repr__(self):
        return "GatewayPayload(op={}, d={}, s={}, t={})".format(self.op, self.d, self.s, self.t)

    def __str__(self):
        return json.dumps(json.loads(self.to_json()), indent=4)