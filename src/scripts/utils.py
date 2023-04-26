def json_to_translation_systems(
        json_dict: dict, algorithms: dict):
    trans_systems = {}
    for name, layers in zip(json_dict.keys(), json_dict.values()):
        layers_converted = []
        for algorithm_name in layers:
            layers_converted.append(algorithms[algorithm_name])
        trans_systems[name] = layers_converted
    return trans_systems


def translation_systems_to_json(
        trans_systems: dict, algorithms_reversed: dict):
    json_dict = {}
    for name, layers in zip(trans_systems.keys(), trans_systems.values()):
        layers_converted = []
        for hashfunc in layers:
            layers_converted.append(algorithms_reversed[hashfunc])
        json_dict[name] = layers_converted
    return json_dict
