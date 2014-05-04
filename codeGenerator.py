import sys
import re

# Attribute object
class Attribute(object):
	def __init__(self, type, name, size=0):
		self.type = type
		self.name = name
		self.size = size

class Function(object):
	def __init__(self, name="", type="", attributes=[]):
		super(Function, self).__init__()
		self.name = name
		self.type = type
		self.attributes = attributes

	def getAttributesLen(self):
		res=0
		for attribute in self.attributes :
			res+=int(attribute.size)
		return res


def parseFile(filename):
	# Read a file
	file = open(filename, "r")
	input = file.readlines()

	print("Parsing "+filename)

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
				new_function.attributes=[] #fix a bug :/
				new_function.name = words[2]

			elif tag == "@type":
				new_function.type = words[2]

			elif tag == "@param":
				type = words[2]
				name = words[-1]
				size = int(words[-2])
				new_function.attributes.append(Attribute(type, name, size))

	if new_function!=None :
		functions.append(new_function)
		new_function = None

	return functions

def generatePython(filename,functions):

	print("Generating python code "+filename)

	# Write a file
	output = ""

	output+="from utils import *\n\n"
	output+="class GeneratedProxy_i2c():\n\n"

	# I2C Register
	output += "i2c_registers = {\n"
	i = 1
	for function in functions:
		output += "	\"REG_" + function.name.upper() + "\":" + str(i) + ",\n"
		i += 1

	output += "}\n\n"


	# Functions definition
	for function in functions:
		output += "def " + function.name + "(self,"
		if function.type == "setter":
			for attribute in function.attributes:
				output += attribute.name + ","

			output = output[:-1] # Remove the last character
			output += "):\n	vals=[]\n"

			for attribute in function.attributes:
				output += "	vals.extend(split_" + attribute.type + "_"+ str(attribute.size) + "(" + attribute.name + "))\n"

			output += "	self.bus.write_block_data(address,i2c_registers['REG_" + function.name.upper() +"'],vals)\n\n"

		elif function.type == "getter":
			output += "):\n"
			output += "	vals=self.bus.read_i2c_block_data(address,i2c_registers['REG_" + function.name.upper() + "']," + str( int(function.getAttributesLen()) ) + ")\n"
			output += "	res=0\n"
			offset = 0
			for attribute in function.attributes:
				output += "	" +attribute.name + "=make_" + attribute.type.replace(" ", "_") + "(vals," + str(offset) + ")\n"
				offset += attribute.size
			output += "	return "
			for attribute in function.attributes:
				output += attribute.name + ","
			output = output[:-1] # Remove the last character
			output +="\n\n"

	#little hack to reindent the file
	output=output.replace("\n", "\n\t")	
	output=output.replace("\tclass", "class")	

	#  Write a file
	file = open(filename, "w")
	file.write(output)
	file.close


functions = parseFile(sys.argv[1])
generatePython(sys.argv[2],functions)