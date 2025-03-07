from jsonschema import validate


def validate_data(data, schema):
    try:
        validate(data, schema)
    except Exception as e:
        raise ValueError(f"Data is invalid: {e}")
    
# TODO: сделать проверку портов