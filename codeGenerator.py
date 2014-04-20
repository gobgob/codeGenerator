import re

# Attribute object
class Attribute(object):
	def __init__(self, type, name, octet=0):
		self.type = type
		self.name = name
		self.octet = octet

class Function(object):
	def __init__(self, name, type, attributes, octet=0):
		super(Function, self).__init__()
		self.name = name
		self.type = type
		self.attributes = attributes
		self.octet = octet

# Read a file
file = open("input.py", "r")
input = file.readlines()

functions = []
attributes = []


for line in input:
	# Parse tags
	if re.match(r"^#\ @(\w+)", line):
		tag = re.match(r"^#\ @(\w+)", line).groups()[0]

		if tag == "method":
			function_name = re.match(r"^#\ @method\ (\w+)", line).groups()[0]

		elif tag == "type":
			function_type = re.match(r"^#\ @type\ (\w+)", line).groups()[0]

		elif tag == "param":
			type = re.match(r"^#\ @param\ ([a-z0-9 ]+) ([a-z_]+)$", line).groups()[0]
			name = re.match(r"^#\ @param\ ([a-z0-9 ]+) ([a-z_]+)$", line).groups()[1]
			if re.search(r"([0-9]+)", line):
				octet = int(re.search(r"([0-9]+)", line).groups()[0]) / 8

			attributes.append(Attribute(type, name, octet))

	# End of function definition
	elif line == "\n":
		octet = 0
		for attribute in attributes:
			octet += attribute.octet # Octet sum for getter definition

		functions.append(Function(function_name, function_type, attributes, octet))
		attributes = []
		function_name = ""
		function_type = ""


# Write a file
output = "i2c_registers = {\n"

# I2C Register
i = 1
for function in functions:
	output += "	\"REG_" + function.name.upper() + "\":" + str(i) + ",\n"
	i += 1

output += "}\n\n"


# Functions definition
for function in functions:
	output += "def i2c_" + function.name + "("
	if function.type == "setter":
		for attribute in function.attributes:
			output += attribute.name + ","

		output = output[:-1] # Remove the last character
		output += "):\n	vals=[]\n"

		for attribute in function.attributes:
			output += "	vals.extend(split_" + attribute.type.replace(" ", "_") + "(" + attribute.name + "))\n"

		output += "	bus.write_block_data(address,i2c_registers['REG_" + function.name.upper() +"'],vals)\n\n"

	elif function.type == "getter":
		output += "):\n"
		output += "	vals=bus.read_i2c_block_data(address,i2c_registers['REG_" + function.name.upper() + "']," + str( int(function.octet) ) + ")\n"
		output += "	res=0\n"
		octet = 0
		for attribute in function.attributes:
			output += "	" +attribute.name + "=make_" + attribute.type.replace(" ", "_") + "(vals," + str( int(octet) ) + ")\n"
			octet += attribute.octet
		output += "	return "
		for attribute in function.attributes:
			output += attribute.name + ","
		output = output[:-1] # Remove the last character


#  Write a file
file = open("output.py", "w")
file.write(output)
