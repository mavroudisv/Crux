import xlrd
from itertools import product

def get_rows(filename, sheet, num_clients, client_id):
	#get num of rows
	num_labels_rows = 3 -1 #it counts from 0
	workbook = xlrd.open_workbook(filename)
	worksheet = workbook.sheet_by_name(sheet)
	num_rows = worksheet.nrows
	num_clean_rows = num_rows - num_labels_rows

	#compute rows for this client
	rows_per_client = num_clean_rows / num_clients
	lower_bound = rows_per_client*client_id + num_labels_rows + 1
	upper_bound = rows_per_client*(client_id+1) + num_labels_rows
	
	#upper_bound = 100
	
	#add residual in the first client
	if ((num_clients -1)==client_id):
		residual = num_clean_rows - (rows_per_client * num_clients)
		upper_bound += residual
	
	#print "from: " + str(lower_bound)
	#print "to: " + str(upper_bound)

	#get labels from these rows
	rows = []	
	for row_index in xrange(worksheet.nrows):
		
		tmp_row_lbl = worksheet.cell(row_index, 1).value #row label
		if (row_index<=upper_bound and row_index>=lower_bound and not tmp_row_lbl == ''):
			rows.append(tmp_row_lbl)

	if ((num_clients-1)==client_id):
		rows.pop() #remove last line, with the average
	
	return rows


#Fetch from the xls cells with matching labels
def read_xls_cell(filename, sheet, column_lbl_1, column_lbl_2, column_lbl_3, row_lbls=[]):
	
	cells = []
	
	workbook = xlrd.open_workbook(filename)
	worksheet = workbook.sheet_by_name(sheet)

	for row_index in xrange(worksheet.nrows):
		for col_index in xrange(worksheet.ncols):

			#row label
			tmp_row_lbl = worksheet.cell(row_index, 1).value

			#column label 1
			tmp_counter = col_index
			tmp_label = ''
			while True:
				tmp_label = worksheet.cell(0, tmp_counter).value
				if tmp_label != '':
					break
				tmp_counter -= 1

			tmp_col_lbl_1 = tmp_label

			#column label 2
			tmp_counter = col_index
			tmp_label = ''
			while True:
				tmp_label = worksheet.cell(1, tmp_counter).value
				if tmp_label != '':
					break
				tmp_counter -= 1
			
			tmp_col_lbl_2 = tmp_label
			
			#column label 3
			tmp_counter = col_index
			tmp_label = ''
			while True:
				tmp_label = worksheet.cell(2, tmp_counter).value
				if tmp_label != '':
					break
				tmp_counter -= 1
		
			#excel treats every num as float and adds .0
			if isinstance(tmp_label, float):
				tmp_col_lbl_3 = str(tmp_label)[:-2]
			else:
				tmp_col_lbl_3 = tmp_label

		
			#print tmp_col_lbl_1,tmp_col_lbl_2,tmp_col_lbl_3,tmp_row_lbl
			if (tmp_col_lbl_1 == column_lbl_1
			 and tmp_col_lbl_2 == column_lbl_2
			 and tmp_col_lbl_3 == column_lbl_3
			 and tmp_row_lbl in row_lbls): #if (row and columns labels) match was found
				cells.append(int(worksheet.cell(row_index, col_index).value)) #add cell to list
				#print int(worksheet.cell(row_index, col_index).value)

	return cells
