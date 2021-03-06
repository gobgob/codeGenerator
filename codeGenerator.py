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

class Flag(object):
	def __init__(self, name, value):
		self.name = name
		self.value = value



def parseFile(filename):
	# Read a file
	file = open(filename, "r")
	input = file.readlines()

	print("Parsing "+filename)

	functions = []
	flags = []
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

			elif tag == "@flag":
				name = words[2]
				value = words[3]
				flags.append(Flag(name, value));

	if new_function!=None :
		functions.append(new_function)
		new_function = None

	return functions, flags


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

			output += "	self.bus.write_block_data(self.address,self.i2c_registers['REG_" + function.name.upper() +"'],vals)\n\n"

		elif function.type == "getter":
			output += "):\n"
			output += "	vals=self.readBlock(self.i2c_registers['REG_" + function.name.upper() + "']," + str( 1+int(function.getAttributesLen()/8) ) + ")\n"
			# output += "	vals=self.bus.read_i2c_block_data(self.address,self.i2c_registers['REG_" + function.name.upper() + "']," + str( 1+int(function.getAttributesLen()/8) ) + ")\n"
			output += "	res=0\n"
			offset = 0
			for attribute in function.attributes:
				output += "	" +attribute.name + "=make_" + attribute.type + "_"+ str(attribute.size) + "(vals," + str(int(offset/8)) + ")\n"
				offset += attribute.size
			output += "	return res,"
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


def typsize2c(type,size):
	the_type=type
	the_type=the_type.replace("integer","int"+str(size)+"_t")
	the_type=the_type.replace("bool","int"+str(size)+"_t")
	return the_type

def generateIno(filename,functions):

	print("Generating arduino/c code "+filename)

	# Write a file
	output = ""
	output += "#include \"proxi2c_generated.h\"\n\n"
	# I2C Register
	output += "enum i2c_registers\n"
	output += "{\n"
	i = 1
	for function in functions:
		output += "	REG_" + function.name.upper() + "=" + str(i) + ",\n"
		i += 1
	output += "};\n\n"

	output +="void i2c_runCmd(int i2c_reg,uint8_t * data_in,uint8_t * data_out,uint8_t * data_out_len)\n"
	output +="{\n"

	output += "\tswitch(i2c_reg) {\n"

	for function in functions:
		output += "\t\tcase REG_" + function.name.upper() + " :\n"
		# output +="Serial.println(\"cmd_"+function.name+"\");\n"
		if function.type == "setter":
			output += "\t\t\tcmd_"+function.name+"( \n"
			offset=0
			for attribute in function.attributes:
				the_type=typsize2c(attribute.type,attribute.size)

				output += "\t\t\tMAKE" + the_type.upper()+"("
				for i in range(0,int((attribute.size)/8)):
					output += "data_in["+str(offset)+"],"
					offset+=1
				output = output[:-1]
				output += "),\n"

			output = output[:-2] # Remove the last character
			output += " \n"
				# //offset += attribute.size

			output += "\t\t\t);\n"

		elif function.type == "getter":
			names=[]
			for attribute in function.attributes:
				the_type=typsize2c(attribute.type,attribute.size)
				names.append("ret_"+function.name+"_"+attribute.name)
				output += "\t\t\t"+the_type+" "+names[-1]+";\n"

			output += "\t\t\tcmd_"+function.name+"( \n"
			for name in names:
				output += "\t\t\t\t&"+name+",\n"
			output = output[:-2]
			output += "\n\t\t\t);\n"
			offset=0
			# output+="uint8_t "+ function.name+"_out[256];\n"
			i=0;
			for attribute in function.attributes:
				the_type=typsize2c(attribute.type,attribute.size)
				output += "\t\t\tSPLIT" + the_type.upper()+"("+names[i]+",data_out,"+str(offset)+");\n"
				# output += "\t\t\tSPLIT" + the_type.upper()+"("+names[0]+","+function.name+"_out,"+str(offset)+");\n"
				offset+=int(attribute.size/8)
				i+=1
			output+="\t\t\t*data_out_len = "+str(offset)+";\n"
			# output+="Wire.write("+ function.name+"_out,"+str(offset)+");\n";
		output += "\t\tbreak;\n"
	output += "\t};\n"
	output += "};\n"
	#  Write a file
	file = open(filename, "w")
	file.write(output)
	file.close

def generateHeader(filename,functions,flags):

	print("Generating arduino/header code "+filename)

	# Write a file
	output = ""

	output +="void i2c_runCmd(int i2c_reg,uint8_t * data_in,uint8_t * data_out,uint8_t * data_out_len);\n"
	for function in functions:
		output += "void cmd_"+function.name+"("
		for attribute in function.attributes:
			the_type=typsize2c(attribute.type,attribute.size)
			if function.type == "setter":
				output += the_type+" "+attribute.name+","
			elif function.type == "getter":
				output += the_type+"* "+attribute.name+","
		output = output[:-1]
		output += ");\n"
	output += "\n"
	for flag in flags:
		output += "#define "+flag.name+" "+flag.value+"\n"

	#  Write a file
	file = open(filename, "w")
	file.write(output)
	file.close



functions,flags = parseFile(sys.argv[1])

out_file = sys.argv[2]

if out_file.find(".py")>0:
	generatePython(out_file,functions)
elif out_file.find(".ino")>0:
	generateIno(out_file,functions)
	generateHeader(out_file.replace(".ino",".h"),functions,flags)
else:
	print("unsupported output file format")