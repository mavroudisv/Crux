import xlrd
from itertools import product


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
