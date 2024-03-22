import json
import os
import sys
from datetime import datetime


LINE1_COMMENT =     "# PY CONNECTOR. Automatically create, dont modify by hand,\n"
LINE2_COMMENT =     "# unless you really know what youre doing!\n"
LINE3_COMMENT_TPL = "# --- Org. filename:{}\n# --- Generation date: {}\n"

arbitrary_code = [
    "# ----dummy----, thats not network\n",
    "def get_jwt():\n",
    "    return 'abcde'\n\n\n",
    "def get_username():\n",
    "    return None\n\n\n",
    "def get_user_id():\n",
    "    return None\n\n\n"
]


def generate_connector_localctx(json_file, output_file) -> int:
    """
    :return: int 1 if process suceeded, 0 otherwise
    """

    try:
        with open(json_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found")
        return 0
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file}'")
        return 0

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    apiname = data['api_name']

    # Status message
    print(f"Generating local context pyConnector for API named {apiname}")
    print(f"At {timestamp}...")
    print()

    with open(output_file, 'w') as f:
        # Write timestamp to the first line of the file
        f.write(LINE1_COMMENT)
        f.write(LINE2_COMMENT)
        f.write(LINE3_COMMENT_TPL.format(output_file, timestamp))
        f.write("import requests\n")
        f.write("import json\n\n\n")

        found_endpoint_url = data['endpoint_url']
        f.write(f"api_url = '{found_endpoint_url}'\n\n\n")

        for line in arbitrary_code:
            f.write(line)

        f.write("class GetResult:\n")
        f.write("    def __init__(self, rawtxt):\n")
        f.write("        self.text = rawtxt\n\n")
        f.write("    def to_json(self):\n")
        f.write("        return json.loads(self.text)\n\n\n")

        f.write("def _ensure_type_hexstr(data):\n")
        f.write("    # Ensure that the provided data is a string containing only hexadecimal characters.\n")
        f.write("    if isinstance(data, str) and all(c in '0123456789abcdefABCDEF' for c in data):\n")
        f.write("        return True\n")
        f.write("    return False\n\n\n")

        f.write("def _get_request(url, given_data=None):\n")
        f.write("    try:\n")
        f.write("        response = requests.get(f\"{api_url}{url}\", params=given_data)\n")
        f.write("        print('sending GET, url:', f\"{api_url}{url}\")\n")
        f.write("        print('sending GET, params:', given_data)\n")
        f.write("        response.raise_for_status()\n")
        f.write("        print('raw result:', response.text)\n")
        f.write("        return GetResult(response.text)\n")
        f.write("    except requests.exceptions.RequestException as e:\n")
        f.write("        print('Error:', e)\n")
        f.write("        return None\n\n\n")

        f.write("# added alias\n")
        f.write("def get(url, data=None):\n")
        f.write("    return _get_request(url, data)\n\n\n")

        f.write("def _post_request(url, given_data=None):\n")
        f.write("    try:\n")
        f.write("        print('sending POST, url:', f\"{api_url}{url}\")\n")
        f.write("        print('sending POST, params:', given_data)\n")
        f.write("        response = requests.post(f\"{api_url}{url}\", json=given_data)\n")
        f.write("        response.raise_for_status()\n")
        f.write("        print('raw result:', response.text)\n")
        f.write("        return GetResult(response.text)\n")
        f.write("    except requests.exceptions.RequestException as e:\n")
        f.write("        print('Error:', e)\n")
        f.write("        return None\n\n\n")

        li_spec_functions = data.get('func_listing', [])
        for func_rank, function in enumerate(li_spec_functions):
            function_name = function.get('name')
            url = function.get('url')
            method = function.get('method')
            parameters = function.get('parameters', [])

            if None in [function_name, url, method]:
                print("Error: Missing required field in API function specification")
                return 0

            f.write(f"def {function_name}(")
            hexparams = set()
            for i, param in enumerate(parameters):
                if param['type'] == 'hexstr':
                    hexparams.add(i)
                    ptype = 'str'
                else:
                    ptype = param['type']
                f.write(f"{param['name']}: {ptype}")
                if i < len(parameters) - 1:
                    f.write(", ")
            f.write("):\n")
            f.write(f"    # {method} request to {url}\n")

            # optional part: testing hexparametrs
            for param_idx in hexparams:
                pname = parameters[param_idx]['name']
                f.write(f"    if not _ensure_type_hexstr({pname}):\n")
                f.write(f"        raise Exception(\"hexstr type not recognized! Value: \"+str({pname}))")
            if len(hexparams) > 0:
                f.write("\n")

            f.write("    try:\n")
            if method == "GET":
                f.write(f"        resobj = _get_request('{url}'")
            elif method == "POST":
                f.write(f"        resobj = _post_request('{url}'")
            else:
                f.write("        # Unsupported method\n")

            if parameters:
                f.write(", {")
                for i, param in enumerate(parameters):
                    f.write(f"'{param['name']}': {param['name']}")
                    if i < len(parameters) - 1:
                        f.write(", ")
                f.write("}")
            f.write(")\n")
            f.write("        return resobj.to_json()\n")
            f.write("    except requests.exceptions.RequestException as e:\n")
            f.write("        print('Error:', e)\n")
            if func_rank == len(li_spec_functions) - 1:
                f.write("        return None\n")
            else:
                f.write("        return None\n\n\n")
        return 1


def proc_autogen_localctx(spec_file='API_SPEC.json', fruit_file="autogened_localctx_connector.py"):
    if os.path.exists(fruit_file):
        print(f"output file already exists ({fruit_file})")
        rez = input('replace? (y/n):')
        while rez not in ('y', 'n'):
            rez = input('replace? (y/n):')
        if rez == 'n':
            print('Aborted!')
            sys.exit(0)
        else:
            os.remove(fruit_file)
            # write file 1
            # generate_connector_localctx(spec_file, '__init__.py')

            # write file2

            if generate_connector_localctx(spec_file, fruit_file):
                print('Ok. Existing file was replaced.')
    else:
        if generate_connector_localctx(spec_file, fruit_file):
            print('Ok. A new file has been created.')


if __name__ == "__main__":
    proc_autogen_localctx()  # used only for testing
