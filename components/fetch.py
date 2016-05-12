import xlrd

def get_rows(filename, sheet, num_relays, relay_id):
    
    #get num of rows
    num_labels_rows = 3
    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_name(sheet)
    num_rows = worksheet.nrows
    num_clean_rows = num_rows - num_labels_rows
    
    #compute rows for this relay
    rows_per_relay = num_clean_rows / num_relays
    
    lower_bound = rows_per_relay*relay_id + num_labels_rows + 1
    upper_bound = rows_per_relay*(relay_id+1) + num_labels_rows
    
    print "from: " + str(lower_bound)
    print "to: " + str(upper_bound)
    
    #add residual in the first relay
    if ((num_relays -1)==relay_id):
        residual = num_clean_rows - (rows_per_relay * num_relays)
        upper_bound += residual
    
    
    #get labels from these rows
    rows = []
    #workbook = xlrd.open_workbook(filename)
    #worksheet = workbook.sheet_by_name(sheet)
    
    from itertools import product
    for row_index in xrange(worksheet.nrows):
        #row label
        tmp_row_lbl = worksheet.cell(row_index, 1).value            
    
        #print tmp_col_lbl_1,tmp_col_lbl_2,tmp_col_lbl_3,tmp_row_lbl
        if (row_index<=upper_bound and row_index>=lower_bound and not tmp_row_lbl == ''):
            rows.append(tmp_row_lbl)
            #print tmp_row_lbl

    
    rows.pop(1) #remove last live, with the average
    
    return rows
    

def give_range(num_relays, num_rows, num_labels_rows, relay_id, is_first=False):
    
    num_clean_rows = num_rows - num_labels_rows
    rows_per_relay = num_clean_rows / num_relays
    
    _from = rows_per_relay*relay_id + num_labels_rows + 1
    _to = rows_per_relay*(relay_id+1) + num_labels_rows
    
    #add residual in the first relay
    if is_first:
        residual = num_clean_rows - (rows_per_relay * num_relays)
        _to += residual

    return (_from, _to)

def read_xls_cell(filename, sheet, column_lbl_1, column_lbl_2, column_lbl_3, lower_bound, upper_bound):
    
    cells = []
    

    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_name(sheet)
    

    from itertools import product
    for row_index in xrange(worksheet.nrows):
        for col_index in xrange(worksheet.ncols):

            #row label
            tmp_row_lbl = worksheet.cell(row_index, 0).value

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
             and row_index<upper_bound
             and row_index>=lower_bound):
                cells.append(worksheet.cell(row_index, col_index).value) #add cell to list

    return cells

def count_rows(filename, sheet):

    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_name(sheet)
    return worksheet.nrows

count_rows('data/data_large.xls','iadatasheet2')

'''
for c in range (5):
    from pprint import pprint
    
    #give_range(num_relays, num_rows, num_labels_rows, relay_id, is_first=False)
    if c < 4:
        pprint(give_range(5, 85, 3, c, False))
    elif c>=4:
        pprint(give_range(5, 85, 3, c, True))
'''

#read_xls_cell('data/data_large.xls','iadatasheet2','Adults in Employment', 'No adults in employment in household: With dependent children','2011',3, 30)
get_rows('data/data_large.xls','iadatasheet2', 1, 0)
