import hdf5storage
import numpy as np

def import_data(file_name):
    """read data from .mat file

    Args:
        file_name (string): the file that going to be read

    Returns:
        np array: the data in the file will be stored in np array format and returned
        this array should be n x 4 x 4 x k x 128 x 8 x 2, where n is the number of people and k is trials number of one columnsn
    """
    mat = hdf5storage.loadmat(file_name)
    data = np.array(mat['All_Feature'][0])
    return data

def delete_data(data,index):
    """delete people

    Args:
        data (np array): the original data
        index ([type]): the index of people going to be deleted

    Returns:
        np array: data after deleting 
    """
    index = sorted(index, reverse=True)
    for i in index:
        data = np.delete(data,i,axis=0)
    return data

def generate_order_diff(data):
    """generate the order difference data and label from original data

    Args:
        data (np array): this array should be n x 4 x 4 x k x 128 x 8 x 2, where n is the number of people and k is trials number of one columnsn
        
    Returns:
        np arrary, np array: This function return two parameters
            the first one is order difference data
            the second one is the label of order difference data
        
        the return data structure is similar as input data, which is n x 1 x 2 x k x 128 x 8 x 2,
        beacause 4 x 4 image types were simplified into only two case of transition negative --> neutral or neutral --> negative
    """
    order_diff = [] #initialize an arrary to store the order difference result
    label = [] #initialize lable to store the label of the order difference
    """
        This part is going to generate the order difference data
        first it loop the each people
        the it loop each row of one people 
        for each row , the order difference is the difference between the average of last two column and the average of first two column
    """
    for people in data: #loop data to generate order difference data
        
        diff_people = [] #initialize an array to store the the order difference data of one people
        diff_row = [] #initialize an array to store the the order difference data of one row 
        label_people = [] #initialize an array to store the the order difference label of one people
        
        for row_index in range(len(people)):
            #loop each row for one people
            row_data = people[row_index]  #store this row in row_data
            #if it is the first row (neutral --> negative) or second row (negative --> neutral)
            # the third row and fourth row will not be considered since there are no emotion transition
            if row_index == 0 or row_index == 1:
                
                second_two_average = (row_data[2]+row_data[3]) #the average of last two column  
                first_two_average = (row_data[1]+row_data[0])  #the average of first two column
                diff = second_two_average - first_two_average  #calculate the difference 
                
                diff_row.append(diff)  #append this result into diff_row
                trials_size = len(diff)  #the number of trials in this row
                
                #if it is the first row, the label as 0 else label as 1 and store in label_people
                if row_index == 0:
                    label_people += [0]*trials_size
                else:
                    label_people += [1]*trials_size
        
        label.append(label_people) 
        diff_people.append(diff_row) 
        order_diff.append(diff_people)
    return np.array(order_diff),np.array(label)

def generate_neg_vs_neu_label(data):
    """generate label of negative vs netural

    Args:
        data (np array): this array should be n x 4 x 4 x k x 128 x 8 x 2, where n is the number of people and k is trials number of one columnsn

    Returns:
        np array: the label of  negative vs netural data
    """
    label = [] #initialized an array to store label
    """
        This part is going to generate the label of negative vs netural
        neutral label as 0 
        negative label as 1
    """
    for people in data:
        #loop each people in original data 
        label_people = []  #initialized an array to store label of one people
        
        for row_index in range(len(people)): #loop each row of one people
            
            for col_index in range(len(people[row_index])):  #loop each column of one row
                
                trials = np.shape(people[row_index][col_index])[0]  #get the number of trials in this column (k) in data
                """
                    if it is the first row and in the first two column
                        or the seoncd row and in the last two column
                        or the thrid row the it is neutral and label as 0
                    eles it is negative and label as 1
                """
                if (row_index == 0 and (col_index == 0 or col_index == 1) ) or \
                    (row_index == 1 and (col_index == 2 or col_index == 3) ) or \
                    row_index == 2:
                    label_people += ([0]*trials)
    
                else:
                    label_people += ([1]*trials)
                    
        label.append(label_people)
        
    return np.array(label)    

def reshape_data(data,data_type = 0):
    """reshape data from n x 4 x 4 x k x 128 x 8 x 2 to m x 2048 (1024) array, 
                where n is the number of people, k is trials number of one columnsn and m is the number of trials of one people ( 4 x 4 x k)
    Args:
        data (np array): [description]
        data_type (int, optional): if data_type == 0 means you want 2048 features all,
                                    else if data_type == 1 means you want the first 1024 features which means 0-4s frequency band
                                    if data_type == 2 means you want the last 1024 features which means 0.5-4.5s frequency band
        . Defaults to 0.

    Returns:
        3 D np array : this is an n x m x 2048 (1024) array , where m is the number of trials of one people (4 x 4 x k) and k is trials number of one columns
    """

    subject = [] #initialize an array to store the result
    for order in range(len(data)): 
        
        people_data = [] #initialize an array to store the result of each people
        temp_data = data[order]
        
        for row_data in temp_data:
            for col_data in row_data:
                for trials in col_data:
                    if data_type == 1:  
                        trials = trials[:,:,0] #choice 0-4s frequency band only 
                    elif data_type == 2:
                        trials = trials[:,:,1] #choice 0.5-4.5s frequency band only
                    #flatten().transpose() reshape the data into 1 D features 2048 or 1024       
                    reshape_trial = trials.flatten().transpose()
                    people_data.append(reshape_trial)
                    
        subject.append(people_data)
        
    return np.array(subject)


def pre_train_data_label(data,label):
    """ convert format for training model
        reshape 3 D array to 2 D array
    Args:
        data (3 D np array: this is an n x m x 2048 (1024) array , where m is the number of trials of one people (4 x 4 x k) and k is trials number of one columns
        label (2 D np array): this is an n x m array  
    Returns:
        np array, np array: the first return value should be 2 D array t x 2048 (1024) where t is the total number of trals for all people
                            the second return value is the label should be 1 D array t x 1
    """
    data_result = data[0]
    label_result = label[0]
    #concate the trails data of all people 
    for index in range(len(data)-1):
        data_result = np.concatenate([data_result,data[index+1]])
        label_result = np.concatenate([label_result, label[index+1]])
    return np.array(data_result), np.array(label_result).reshape(-1,1)

def generate_test_neu_vs_neg_data(data,data_type=0):

    return_data = []
    return_label = []
    for people in data:
        neutral = people[0][0]
        neutral = np.concatenate([neutral, people[0][1]])
        negative = people[1][0]
        negative = np.concatenate([negative, people[1][1]])
        neutral = np.concatenate([neutral,people[1][2]])
        neutral = np.concatenate([neutral,people[1][3]])
        negative = np.concatenate([negative,people[0][2]])
        negative = np.concatenate([negative,people[0][3]])
        np.random.shuffle(neutral)
        np.random.shuffle(negative)
        neutral = neutral[0:18]
        negative = negative[0:18]
        temp_data = np.concatenate([neutral,negative])
        temp_label = np.concatenate([[0]*18,[1]*18])
        return_data.append([[temp_data]])
        return_label.append([[temp_label]]) 
    return np.array(return_data),np.array(return_label)        

