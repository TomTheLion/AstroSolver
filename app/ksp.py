# ksp conversion

def from_ksp(structure):
    if type(structure) is not dict:
        return structure

    if structure["$type"] == "kOS.Safe.Encapsulation.Lexicon":
        output = {}
        lexicon_list = structure["entries"]
        for i in range(0, len(lexicon_list), 2):
            output[lexicon_list[i]] = from_ksp(lexicon_list[i + 1])

    elif structure["$type"] == "kOS.Safe.Encapsulation.ListValue":
        output = from_ksp(structure["items"])

    elif structure["$type"] == "kOS.Suffixed.TimeSpan":
        output = structure["span"]

    elif structure["$type"] == "kOS.Suffixed.Vector":
        output = [structure["x"], structure["y"], structure["z"]]

    else:
        output = structure

    return output

def to_ksp_lexicon(structure):
    ksp_lexicon = {
        "entries": [],
        "$type": "kOS.Safe.Encapsulation.Lexicon"
    }

    for key, value in structure.items():
        ksp_lexicon["entries"].append(key)
        ksp_lexicon["entries"].append(value)

    return ksp_lexicon

def to_ksp_list(structure):
    ksp_list = {
        "items": structure,
        "$type": "kOS.Safe.Encapsulation.ListValue"
    }

    return ksp_list

def to_ksp_vector(structure):
    ksp_vector = {
        "x": structure[0],
        "y": structure[1],
        "z": structure[2],
        "$type": "kOS.Suffixed.Vector"
    }

    return ksp_vector