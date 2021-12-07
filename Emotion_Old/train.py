import numpy as np
from sklearn.pipeline import Pipeline
from preprocessing_data import *
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

"""
    The reason to use 3D data as input rather than use 2D is 
    we can split data by the number of people so we can do cross subject and within subject
    in 2D array we don't know which row belongs to which person 
"""

#cross subject validation
def cross_subject(model,data,label,clf="l1",data_type = 0):
    """cross subject validation

    Args:
        model (training model): the model that going to be validated in cross subject validation
        data (3D array): this is an n x m x 2048 (1024) array , where m is the number of trials of one people (4 x 4 x k) and k is trials number of one columns
        label (2D array): this is an n x m array

    Returns:
        [list]: the accuracy of each subject in cross subject validation
    """    
    accuracy = []   #initialize an arary to store the accuracy of each subject
    if data_type == 0: 
        coeff = [0] * 2048
    else:
        coeff = [1]* 1024
    #loop for the whole data 
    for test_index in range(len(data)):
        train_index = list(range(len(data)))
        train_index.remove(test_index)
        test_index = [test_index]
        test_data, test_label = pre_train_data_label(data[test_index],label[test_index] )
        train_data, train_label = pre_train_data_label(data[train_index], label[train_index])
        model.fit(train_data,train_label.ravel())
        score = model.score(test_data,test_label.ravel())
        accuracy.append(score)
        if clf=="l1":
            coeff1 = np.add(coeff, model.named_steps['clf'].coef_[0])
            coeff=coeff1
    return accuracy,coeff

#within subject validation
def within_subject(model,data,label,clf="l1",data_type = 0):
    
    """within subject validation

    Args:
        model (training model): the model that going to be validated in within subject validation
        data (3D array): this is an n x m x 2048 (1024) array , where m is the number of trials of one people (4 x 4 x k) and k is trials number of one columns
        label (2D array): this is an n x m array

    Returns:
        [list]: the accuracy of each subject in within subject validation
    """
    
    accuracy = []  #initialize an arary to store the accuracy of each subject 
    if data_type == 0: 
        coeff = [0] * 2048
    else:
        coeff = [1]* 1024
    for within_index in range(len(data)):
        
        within_data = data[[within_index]]
        within_label = label[[within_index]]
        data_pre_trained, label_pre_trained = pre_train_data_label(within_data,within_label)
        within_accuracy = [] 
        
        for test_index in range(len(data_pre_trained)):
            
            train_index = list(range(len(data_pre_trained)))
            train_index.remove(test_index)
            train_data, train_label =  data_pre_trained[train_index],label_pre_trained[train_index]
            test_data, test_label =  data_pre_trained[test_index],label_pre_trained[test_index]     
            model.fit(train_data,train_label.ravel())
            score = model.score(test_data.reshape(1, -1),test_label.ravel())
            within_accuracy.append(score)
            if clf == "l1":
                coeff1 = np.add(coeff, model.named_steps['clf'].coef_[0])
                eff=coeff1
        accuracy.append(sum(within_accuracy)/len(within_accuracy))
        
    return accuracy,coeff   

def logistic_cross_validation(data,label,cv="cross",data_type = 0):
    
    """logistic regression: Use logistic regression with cross subject validation or within subject validation
    
    Args:
        data (3D array): this is an n x m x 2048 (1024) array , where m is the number of trials of one people (4 x 4 x k) and k is trials number of one columns
        label (2D array): this is an n x m array
        cv (string):
            if cv == cross means use cross subject validation
            if cv == within means use within subject validation
        
    Returns
        list:the accuracy of each subject return by the corresponding validation

    """
    #This step build a pipleline that standarize the data first ,then fit the data into logistic regression with maximum of 500 iteration
    model = Pipeline([
                    ('scale', StandardScaler()),
                    ('clf', LogisticRegression(max_iter=500))
                    ])
    
    """
        if cv == cross: means use cross subject validation
            then calculate the average accuracy of cross subject validation and print it
            and return the accuracy of each subject
        if cv == within: means use within subject validation
            then calculate the average accuracy of within subject validation and print it
            and return the accuracy of each subject
        otherwise exit the program and hint to input correct cv 
    """
    
    if cv == "cross":  
        acc_array, coeff = cross_subject(model,data,label,clf="logistic",data_type = data_type)
        acc =sum(acc_array)/len(acc_array)
        return acc_array
    elif cv == "within":
        acc_array,coeff = within_subject(model,data,label,clf="logistic",data_type = data_type)
        acc =sum(acc_array)/len(acc_array)
        return acc_array
    else:
        print("Invalid cv method, please chose cross or within ")
        exit()

def logistic_regularize_search_model(data,label, clf = "l1", Solver='liblinear',strength=[1],cv="cross",data_type = 0):
    """search the best parameters and model for l1 regularization

    Args:
        data (3D array): this is an n x m x 2048 (1024) array , where m is the number of trials of one people (4 x 4 x k) and k is trials number of one columns
        label (2D array): this is an n x m array
        Solver (str, optional): method to solve for l1 regularization ‘liblinear’ or ‘saga. Defaults to 'liblinear'.
        strength (list, optional): a list of regression strength to search nomalr from [0.01,0.1,1,10,100]. Defaults to [1].
        cv (str, optional): method for validation cross or within. Defaults to "cross".

    Returns:
        mode, int, int: the best model, the best regularization strength, the best accuracy,the best accuracy array of each person
    """
    
    #initialize parameters
    best_accuracy = 0
    best_model = None
    best_strength = 0
    best_acc_array = []
    #for each strength in the strength list
    for c in strength:
        temp_acc = 0
         #This step build a pipleline that standarize the data first ,then fit the data into logistic regression with maximum of 500 iteration and the parameters as input
        model = Pipeline([
                        ('scale', StandardScaler()),
                        ('clf', LogisticRegression(solver=Solver,penalty=clf,C=c,max_iter=500))
                        ])
    
        """
            if cv == cross: means use cross subject validation
                then calculate the average accuracy of cross subject validation and print it
                and return the accuracy of each subject
            if cv == within: means use within subject validation
                then calculate the average accuracy of within subject validation and print it
                and return the accuracy of each subject
            otherwise exit the program and hint to input correct cv 
        """
        if cv == "cross":
            temp_acc_array,coeff = cross_subject(model,data,label,clf=clf,data_type = data_type)
            temp_acc =sum(temp_acc_array)/len(temp_acc_array)
        elif cv == "within":
            temp_acc_array,coeff = within_subject(model,data,label,clf=clf,data_type = data_type)
            temp_acc = sum(temp_acc_array)/len(temp_acc_array)
        else:
            print("Invalid cv method, please chose cross or within ")
            exit()
        #if temp_acc > then best_accuracy, then replace it as the best_arracy
        if temp_acc > best_accuracy:
            best_accuracy = temp_acc
            best_model = model
            best_strength = c
            best_acc_array = temp_acc_array
    return best_model,best_strength,best_accuracy,best_acc_array,coeff

def random_forest_predict(data,label,n_estimators=150,max_depth=None,cv = "cross",data_type = 0):
    """Use random forest with cross subject validation or within subject validation

    Args:
        data (3D array): this is an n x m x 2048 (1024) array , where m is the number of trials of one people (4 x 4 x k) and k is trials number of one columns
        label (2D array): this is an n x m array
        n_estimators (int, optional): The number of trees in the forest.. Defaults to 150.
        max_depth ([type], optional): The maximum depth of the tree.. Defaults to None.
        cv (str, optional): method for validation cross or within. Defaults to "cross".

    Returns:
        list:the accuracy of each subject return by the corresponding validation
    """
    #create randomforest model

    model = Pipeline([('clf',RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth))])
    """
        if cv == cross: means use cross subject validation
            then calculate the average accuracy of cross subject validation and print it
            and return the accuracy of each subject
        if cv == within: means use within subject validation
            then calculate the average accuracy of within subject validation and print it
            and return the accuracy of each subject
        otherwise exit the program and hint to input correct cv 
    """

    if cv == "cross":
        acc_array,coeff = cross_subject(model,data,label,clf="random",data_type = data_type)
        acc =sum(acc_array)/len(acc_array)
        return acc_array
    elif cv == "within":
        acc_array,coeff = within_subject(model,data,label,clf="random",data_type = data_type)
        acc =sum(acc_array)/len(acc_array)
        return acc_array
    else:
        return

def generate_diff(data,clf = "l1",Solver='liblinear',strength=[1],cv="cross",data_type = 0):
    """generate the order difference result

    Args:
        data (np array): the data after reading from .mat file
        Solver (str, optional): the solver going to be usedin l1 regularization. Defaults to 'liblinear'.
        strength (list, optional): the regularization strength in l1 penalty. Defaults to [1].
        cv (str, optional): cross subject  if "cross", within subject if cv = "within". Defaults to "cross".
    """
    #generate order difference data 
    order_diff_data,order_diff_label = generate_order_diff(data)
    #reshape data to 3D array 
    order_diff_data = reshape_data(order_diff_data,data_type=data_type)
    #find the best parameter for logistic regression with l1 regularization 
    diff_best_model,diff_best_strength,diff_best_accuracy,diff_best_accuracy_array,coeff = logistic_regularize_search_model(order_diff_data,order_diff_label,Solver=Solver, clf = "l1",strength=strength,cv=cv,data_type = data_type)

    #get the result of logistic regression
    diff_logistic_accuracy = logistic_cross_validation(order_diff_data,order_diff_label, cv=cv,data_type= data_type)
    # #get the result of random foreset
    diff_random_forest_accuracy = random_forest_predict(order_diff_data,order_diff_label,cv=cv,data_type= data_type)
    return diff_best_accuracy_array,diff_logistic_accuracy,diff_random_forest_accuracy,coeff

def generate_neutral_vs_negative(data,Solver='liblinear',clf = "l1",strength=[1],cv="cross",data_type=0):
    """generate the neutral vs negative result

    Args:
        data (np array): the data after reading from .mat file
        Solver (str, optional): the solver going to be usedin l1 regularization. Defaults to 'liblinear'.
        strength (list, optional): the regularization strength in l1 penalty. Defaults to [1].
        cv (str, optional): cross subject  if "cross", within subject if cv = "within". Defaults to "cross".
    """
    #generate order difference data 
    vs_label = generate_neg_vs_neu_label(data)
    #reshape data to 3D array
    vs_reshape = reshape_data(data)
    #find the best parameter for logistic regression with l1 regularization 
    vs_best_model,vs_best_strength,vs_best_accuracy,vs_best_accuracy_array, coeff = logistic_regularize_search_model(vs_reshape,vs_label,clf = clf,Solver=Solver, strength=strength,cv=cv,data_type= data_type)
    vs_logistic_accuracy = logistic_cross_validation(vs_reshape,vs_label,cv=cv,data_type= data_type)
    vs_random_forest_accuracy = random_forest_predict(vs_reshape,vs_label,cv=cv,data_type= data_type)

    return vs_best_accuracy_array,vs_logistic_accuracy,vs_random_forest_accuracy

def generate_test_neu_vs_neg(data,Solver='liblinear',clf = "l1",strength=[1],cv="cross",data_type = 0):
    order_diff_data,order_diff_label = generate_test_neu_vs_neg_data(data)
    order_diff_data = reshape_data(order_diff_data)
    diff_best_model,diff_best_strength,diff_best_accuracy,diff_best_accuracy_array, coeff = logistic_regularize_search_model(order_diff_data,order_diff_label,clf =clf, Solver=Solver, strength=strength,cv=cv,data_type= data_type)
    diff_logistic_accuracy = logistic_cross_validation(order_diff_data,order_diff_label, cv=cv,data_type= data_type)
    diff_random_forest_accuracy = random_forest_predict(order_diff_data,order_diff_label,cv=cv,data_type= data_type)
    return diff_best_accuracy_array,diff_logistic_accuracy,diff_random_forest_accuracy

def split_group_stress(data,stress,number_group):
    data = np.array(data)
    index = np.array(sorted(range(len(stress)), key=lambda k: stress[k]))
    if number_group == 3 and len(stress) == 40:
        split_index = [index[0:14],index[14:28],index[28:40]]
    else:
        split_index = np.array_split(index,number_group)
    result = []
    for item in split_index:
        split_data = data[item]
        result.append(split_data)
    return result, split_index

def re_rank_result(result,group_index):
    index = np.array(sorted(range(len(group_index)), key=lambda k: group_index[k]))
    new_result = []
    for i in index:
       new_result.append(result[i]) 
    return new_result