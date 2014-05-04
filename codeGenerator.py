import re

# Attribute object
class Attribute(object):
	def __init__(self, type, name, octet=0):
		self.type = type
		self.name = name
		self.octet = octet

class Function(object):
	def __init__(self, name="", type="", attributes=[]):
		super(Function, self).__init__()
		self.name = name
		self.type = type
		self.attributes = attributes


# Read a file
file = open("input.py", "r")
input = file.readlines()

functions = []
new_function = None

for line in input:
	# Parse tags
	if re.match(r"^#\ @(\w+)", line):
		words=line.split();
		tag=words[1]

		if tag == "@method":
			if new_function!=None :
				functions.append(new_function)
				new_function = None
			new_function=Function()
			new_function.name = words[2]

		elif tag == "@type":
			new_function.type = words[2]

		elif tag == "@param":
			type = words[2]
			name = words[-1]
			octet = words[-2]
			new_function.attributes.append(Attribute(type, name, octet))

if new_function!=None :
	functions.append(new_function)
	new_function = None


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
