import xml.etree.ElementTree as et

def untranslate(string):
	a='asdf'
	str = string
	if type(string) != type(a):
		return ''
	str = str.replace('\\_', '_')
	str = str.replace('\\textsuperscript', '^')
	str = str.replace('$', 'dollar')
	return str

def translate(string):
	str = ''
	if type(string) != type(str):
		return ''

	s = string.split('$')
	i=0
	while i < len(s):
		if i%2 == 0:
			s[i] = s[i].replace('_', '\\_')
			s[i] = s[i].replace('^', '\\textsuperscript')
		else:
			s[i] = '$'+s[i]+'$'
		str += s[i]
		i+=1
	
	return str

tree = et.parse('Registry.xml')
root = tree.getroot()

package_names = {}
packages = root.find('packages')
for package in packages:
	package_names[package.get('name')] = package.get('longname')

f = open('chap_fields.tex', 'w')
f.write('\\chapter{Description of Model Fields}\n')
f.write('\\label{chap:atm_fields}\n')
f.write("Every field that may be read or written in a NetCDF {\\em stream} (as described in Chapter \\ref{chap:mpas_io}) by the MPAS-Atmosphere model is described in this chapter. The dimensionality of each field is given in Fortran storage order (i.e., the fastest-varying dimension is inner-most).\n")
f.write ('\\small\n')

#	Loop through the var structs/ var arrays
var_list = []
for child in root:
	if child.tag != 'var_struct':
		continue

	struct_name = translate(child.get('name'))
	for el in child:

		# Case 1, var_array as opposed to var_struct
		if el.tag == 'var_array':
			arr_name = translate(el.get('name'))
			code_name = translate(el.get('name_in_code'))
			if len(code_name) == 0:
				code_name = arr_name 
			t = translate(el.get('type'))
			d = translate(el.get('dimensions'))
			var_arr = [arr_name, t, d, struct_name, code_name]
			var_arr_list = []
			for c in el:
				ps = []
				if c.get('packages') != None:
					ps = c.get('packages').split(';', c.get('packages').count(';'))
				field_name = translate(c.get('name'))
				units = translate(c.get('units'))
				desc =  translate(c.get('description'))
				group = translate(c.get('array_group'))
				var_arr_list.append((field_name, units, desc, ps, group))
				var_list.append((field_name, arr_name)) # Put a 2-element tuple in var_list that will become the link to the actual field description as a constituent of its array
			var_arr.append(var_arr_list) # var_arr is a list object that represents the field array (like 'aerosols'), and the var_arr_list is a list of var objects that are its constituents
			var_list.append(var_arr) # add the var array to the var list
			continue
		elif el.tag != 'var':
			continue

		# Case 2, just a var_struct not a var_array
		ps = []
		if el.get('packages') != None:
			ps = el.get('packages').split(';', el.get('packages').count(';'))

		field_name = translate(el.get('name'))
		code_name = translate(el.get('name_in_code'))
		if len(code_name) == 0:
			code_name = field_name
		units = translate(el.get('units'))
		desc =  translate(el.get('description'))
		t = translate(el.get('type'))
		d = translate(el.get('dimensions'))

		var_list.append((field_name, t, d, units, desc, ps, struct_name, code_name))

var_list.sort(key=lambda v: v[0])

f.write('\n\\renewcommand{\\arraystretch}{1.5}\n\\def\\bsq#1{\\lq{#1}\\rq}')



# For inserting phantom sections
# First determine how many fields start with each letter
counts = {}
for c in range(ord('a'), ord('z')+1):
	counts[chr(c)] = 0
for var in var_list:
	if type(var) == list:
		counts[var[0][0]] += len(var)
	else:
		counts[var[0][0]] += 1

# Then tally the total number and divide by 4 
num = 0
for k,v in counts.items():
	num = num+v
num = num // 4

# Find the section cutoffs, rounded to teh nearest letter
letters = ['A']
x = 0
for k in sorted(counts.keys()):
	v = counts[k]
	if v == 0:
		continue
	if x <= num and x + v >= num: #found the 2 letters that straddle the section size
		# pick the one that causes the section to be closest to 'num'
		if num - x < x + v - num:
			letters.append(chr(ord(k) - 1))
			letters.append(k)
			x = 0
		else:
			letters.append(k)
			letters.append(chr(ord(k) + 1))
			x = 0
			continue
	x += v

letters.append('Z') # last section goes to Z even if there are no z variables
# Convert to capital letters (means one fewer cap<->lowercase conversion)
for i in range(len(letters)):
	c = letters[i]
	if (ord(c) > 90):
		letters[i] = chr(ord(c) - 32) 
			
#manaully put in the first section, then loop through
f.write('\n\\phantomsection\n')
f.write('\\addcontentsline{toc}{section}{Fields A--'+letters[1]+'}\n\n')
i = 2
for var in var_list:
	if i < len(letters)-1: # means there is still an un-done section
		# if the first letter of the current variable being printed is the target letter or 
		# the lowercase version of the target letter, insert the phantom section and increment to the next target letter
		if var[0][0] == letters[i] or var[0][0] == chr(ord(letters[i]) + 32):
			f.write('\n\\phantomsection\n')
			f.write('\\addcontentsline{toc}{section}{Fields '+letters[i]+'--'+letters[i+1]+'}\n\n')
			i += 2
	# current variable being printed is just a link to the var_array constituent it represents
	if len(var) == 2:
		f.write('\n\\vspace{10mm}\n\\noindent\\hyperlink{'+untranslate(var[1])+'}{\\color{red}{\\textbf{\\large{' + var[0] + '}} --- \\textit{see \\bsq{' + var[1] + '}}}}\n')
		continue

	# variable to be printed is a var_array
	if type(var) == list:
		f.write('\n\\vspace{10mm}\n\\noindent\\begin{minipage}{\\textwidth}\n\\hypertarget{'+untranslate(var[0])+'}\n')
		f.write('\\noindent\\textbf{\\Large{' + var[0] + '}} (' + var[1] + ') (' + var[2].replace(' ', ', ') + ') \\\\ \n')
		f.write('\\begin{tabular}{|p{.3\\textwidth-2\\tabcolsep} |p{.7\\textwidth-2\\tabcolsep} |} \\hline\n')
		f.write('Description & \\textit{\\bsq{'+var[0]+'} is a variable array used in code which is made up of the constituent fields listed below.} \\\\ \\hline\n')
		f.write('Accessed in code & as \\bsq{' + var[4] + '} from the \\bsq{'+var[3]+'} pool \\\\ \\hline\n')
		f.write('\\end{tabular} \n\\end{minipage}\n')
		f.write('\n\\vspace{5mm}\n\\noindent Contains constituents:\n')

		# for each constituent...
		for cvar in var[5]:
			f.write('\n\\vspace{10mm}\n\\hspace{.1\\textwidth}\\noindent\\begin{minipage}{.9\\textwidth}\n\\hypertarget{'+untranslate(cvar[0])+'}\n')
			f.write('\\noindent\\textbf{\\normalsize{' + cvar[0] + '}} --- \\textit{constituent field of var\_array \\textbf{'+var[0]+'}}  \\\\ \n')
			f.write('\\begin{tabular}{|p{.25\\textwidth-.5\\tabcolsep} |p{.65\\textwidth-1.3\\tabcolsep} |} \\hline\n')
			f.write('Description & \\textit{'+cvar[2]+'} \\\\ \\hline\n')
			f.write('Units & \\textit{' + cvar[1] + '} \\\\ \\hline\n')
			f.write('Array Group & ' + cvar[4] + ' \\\\ \\hline\n')
			if len(cvar[3]) > 0:
				ln = 'Allocated by & '
				for p in cvar[3]:
					ln += translate(p)
					ln += ', '
				ln = ln[0:-2] + ' \\\\ \\hline\n'
				f.write(ln)
			f.write('\\end{tabular} \n\\end{minipage}\n')
		continue

	# variable to be printed is a var_struct
	f.write('\n\\vspace{10mm}\n\\noindent\\begin{minipage}{\\textwidth}\n\\hypertarget{'+untranslate(var[0])+'}\n')
	f.write('\\noindent\\textbf{\\large{' + var[0] + '}} (' + var[1] + ') (' + var[2].replace(' ', ', ') + ') \\\\ \n')
	f.write('\\begin{tabular}{|p{.3\\textwidth-2\\tabcolsep} |p{.7\\textwidth-2\\tabcolsep} |} \\hline\n')
	f.write('Units & \\textit{' + var[3] + '} \\\\ \\hline\n')
	f.write('Description & \\textit{' + var[4] + '} \\\\ \\hline\n')
	if len(var[5]) > 0:
		ln = 'Allocated by & '
		for p in var[5]:
			ln += translate(p)
			ln += ', '
		ln = ln[0:-2] + ' \\\\ \\hline\n'
		f.write(ln)
	f.write('Accessed in code & as \\bsq{' + var[7] + '} from the \\bsq{' + var[6] +'} pool \\\\ \\hline\n')
	f.write('\\end{tabular} \n\\end{minipage}\n')

f.close()
print("Done with chap_fields.tex")
