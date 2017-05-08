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
	a='asdf'
	str = ''
	if type(string) != type(a):
		return ''

	s = string.split('$')
	i=0
	while i < len(s):
		if i%2 == 0:
			s[i] = s[i].replace('_', '\\_')
			s[i] = s[i].replace('^', '\\textsuperscript')
			s[i] = s[i].replace('ampersand', '\\&')
			s[i] = s[i].replace('&', '\\&')
		else:
			s[i] = '$'+s[i]+'$'
		str += s[i]
		i+=1
	
	return str

def parseRegistry(filename):
	tree = et.parse(filename)
	root = tree.getroot()

	registry = []
	for child in root:
		if child.tag != 'nml_record':
			continue
		var_list = []
		for var in child:
			if var.tag != 'nml_option':
				print('bad tag, '+var.tag)
				continue
			var_list.append((translate(var.get('name')), translate(var.get('type')), translate(var.get('default_value')), translate(var.get('units')), translate(var.get('description')),  translate(var.get('possible_values')), child.get('in_defaults') == 'false' if child.get('in_defaults') == 'false' else var.get('in_defaults') == 'false'))
		registry.append((translate(child.get('name')), var_list))
	return registry


# First do the model namelist options
reg = parseRegistry('Registry.xml')
f = open('chap_model_namelist.tex', 'w')
f.write('\\chapter{Model Namelist Options}\n\\label{chap:atm_namelist}\n')
f.write('This chapter summarizes the complete set of namelist options available when running the MPAS non-hydrostatic atmosphere model. All date-time string specifications are of the form described at the beginning of Appendix \\ref{chap:init_atm_namelist}.\n')
f.write('\\renewcommand{\\arraystretch}{1.5}\n')

# for each namelist record (section)
for sec in reg:

	f.write('\\hypertarget{mrec:'+untranslate(sec[0])+'}{}\n')
	f.write('\\section{'+sec[0]+'}\n\\small\n')

	# Description of tuple 'sec'	
	# sec[0] = nml_record name
	# sec[1] = list of namelist options in that record (each element is a list of details about the namelist option)

	# for each namelist option in section
	for var in sec[1]:
		f.write('\n\\vspace{10mm}\n\\noindent\\begin{minipage}{\\textwidth}\n\\hypertarget{mnl:'+untranslate(var[0])+'}\n')
		f.write('\\noindent\\textbf{\\large{' + var[0] + '}} (' + var[1] + ') \\\\ \n')
		f.write('\\begin{tabular}{|p{.3\\textwidth-2\\tabcolsep} |p{.7\\textwidth-2\\tabcolsep} |} \\hline\n')
		f.write('Units & \\textit{' + var[3] + '} \\\\ \\hline\n')
		f.write('Description & \\textit{' + var[4] + (' (hidden by default)' if var[6] else '') + '} \\\\ \\hline\n')
		f.write('Possible Values & '+var[5]+' \\textit{(default: ' + var[2] + ')} \\\\ \\hline\n')
		f.write('\\end{tabular} \n\\end{minipage}\n')

#		Description of list 'var'
#		var[0] = namelist option name
#		var[1] = namelist option data type
#		var[2] = default value
#		var[3] = units
#		var[4] = description
#		var[5] = option is hidden by default (T or F)

f.close()
print("Done with chap_model_namelist.tex")

# Then do the initialization namelist options
reg = parseRegistry('Registry_init.xml')
f = open('chap_init_namelist.tex', 'w')
f.write('\\chapter{Initialization Namelist Options}\n\\label{chap:init_atm_namelist}\n\n\\def\\bsq#1{\\lq{#1}\\rq}')
f.write('This chapter summarizes the complete set of namelist options available when running the MPAS non-hydrostatic atmosphere initialization core.  The applicability of certain options depends on the type of initial conditions to be created --- idealized or \\bsq{real-data} --- and such applicability is identified in the description when it exists.\n\n Date-time strings throughout all MPAS namelists assume a common format. Specifically, time intervals are of the form {\\tt \\bsq{[DDD\_]HH:MM:SS[.sss]}}, where {\\tt DDD} is an integer number of days with any number of digits, {\\tt HH} is a two-digit hour value, {\\tt MM} is a two-digit minute value, {\\tt SS} is a two-digit second value, and {\\tt sss} are fractions of a second with any number of digits; any part of the time interval format in square brackets ({\\tt [ ]}) may be omitted, and if days are omitted, {\\tt HH} may be either a one- or two-digit hour specification.  Time instants (e.g., start time or end time) are of the form {\\tt \\bsq{YYYY-MM-DD[\_HH:MM:SS[.sss]]}}, where {\\tt YYYY} is an integer year with any number of digits, {\\tt MM} is a two-digit month value, {\\tt DD} is a two-digit day value, and {\\tt HH:MM:SS.sss} is a time with the same format as in a time interval specification. For both time instants and time intervals, a value of {\\tt \\bsq{none}} represents \\bsq{no value}.\n\n')
f.write('\\renewcommand{\\arraystretch}{1.5}\n')

# for each namelist record (section)
for sec in reg:
	
	f.write('\\hypertarget{irec:'+untranslate(sec[0])+'}{}\n')
	f.write('\\section{'+sec[0]+'}\n\\small\n')

	# for each namelist option in section
	for var in sec[1]:
		f.write('\n\\vspace{10mm}\n\\noindent\\begin{minipage}{\\textwidth}\n\\hypertarget{inl:'+untranslate(var[0])+'}\n')
		f.write('\\noindent\\textbf{\\large{' + var[0] + '}} (' + var[1] + ') \\\\ \n')
		f.write('\\begin{tabular}{|p{.3\\textwidth-2\\tabcolsep} |p{.7\\textwidth-2\\tabcolsep} |} \\hline\n')
		f.write('Units & \\textit{' + var[3] + '} \\\\ \\hline\n')
		f.write('Description & \\textit{' + var[4] + (' (hidden by default)' if var[6] else '') + '} \\\\ \\hline\n')
		f.write('Possible Values & '+var[5]+' \\textit{(default: ' + var[2] + ')} \\\\ \\hline\n')
		f.write('\\end{tabular} \n\\end{minipage}\n')
f.close()
print("Done with chap_init_namelist.tex")
