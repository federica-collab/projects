
import json
import jsonschema
from jsonschema import validate


regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'

fdd_schema = {"title": "FDD Request",
    "description": "Request for the fdd algorithm.",
    "type" : "object",
    "required": ["device_id","time_min","time_max","axis"],
    "properties" : {
        "device_id" : {"type" : "array",
  "items": {
    "type": "integer"
  }},
        "time_min" : {"type" : "string","format": "date","pattern":regex},
        "time_max" : {"type" : "string","format": "date","pattern":regex},
        "axis" : {"type" : "array",
  "items": {
    "type": "string",
  "minItems": 1,
  "maxItems": 3,
  "enum": ["x", "y", "z"]}},
  "filtering": {
    "enum": ["bandpass", "lowpass"]
  }
},
"if": {
  "properties": { "filtering": { "const": "lowpass" } }
},
"then": {"required":["fmin","order"],
  "properties": { "fmin": { "type": "number","minimum": 1 }, "order":{ "type": "integer","minimum": 1 } }
},
"else": {"required":["fmin","fmax","order"],
  "properties": { "fmin": { "type":"number","minimum": 1 },"fmax": { "type":"integer","minimum": 1 }, "order":{ "type": "integer","minimum": 1 }}
},
"return_acc":{"type": "integer"}}
# fdd_schema
# my_json = json.loads('{"device_id":[1042],"time_min": "2019-08-10T07:48:00.000Z","time_max": "2019-08-10T07:58:00.000Z","axis":["x","y","z"],"filtering":[{"kind":"bandpass"},{"range_min":-1},{"range_max":10},{"order":4}],"return_acc":1}')
#
# validate(instance=my_json, schema=fdd_schema)
# my_json = json.loads('{"ids":2000000,"filtering":[{"kind":"bandpass"},{"range_min": 5},{"range_max":10},{"order":4}]}')
# my_json
displacemt_ids_schema = {"title": "displacement ids",
"description": "Request for displacemt and velocity calculation",
"type": "object",
"required": ["ids", "filtering"],
"properties": {"ids":{"type": "integer"},
"filtering":{
  "enum": ["bandpass", "lowpass"]
}},
"if": {
"properties": { "filtering": { "const": "lowpass" } }
},
"then": {"required":["fmin","order"],
"properties": { "fmin": { "type": "number","minimum": 1 }, "order":{ "type": "number","minimum": 1 } }
},
"else": {"required":["fmin","fmax","order"],
"properties": { "fmin": { "type":"number","minimum": 1 },"fmax": { "type":"integer","minimum": 1 }, "order":{ "type": "integer","minimum": 1 }}
},
"range_min":{"type":"integer"}, "range_max":{"type":"integer"}, "order":{"type":"integer"}
}

displacemt_device_schema = {"title": "displacement device",
"description": "Request for displacemt and velocity calculation",
"type": "object",
"required": ["device_id","time_min","time_max","timestep"],
"properties" : {
"device_id" : {"type" : "integer",
},
    "time_min" : {"type" : "string","format": "date","pattern":regex},
    "time_max" : {"type" : "string","format": "date","pattern":regex},
    "timestep": {"type" : "integer"}
},
}

psd_schema = {"title": "PSD Request",
"description": "Request for PSD",
"type": "object",
"required": ["device_id","time_min","time_max"],
"properties" : {
"device_id" : {"type" : "integer",
},
    "time_min" : {"type" : "string","format": "date","pattern":regex},
    "time_max" : {"type" : "string","format": "date","pattern":regex},
},
}
