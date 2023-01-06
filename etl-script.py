def extract_balancesSheet_variables(metric, allFilesExtracted:dict):
    
    '''
    metric: user-defined metric; e.g. Current Ratio = (AssetsCurrent - totalInventory) / totalLiabilities
    
    allFilesExtracted: key: company names; values: Json data structure from SEC filing data
    '''
    
    # import pandas to transform parsed data structure into a Dataframe
    from pandas import DataFrame as pd_df
    
    # a local library for plotting 
    from plot import plotTemplate
    
    # create dictionary with keys: names of companies wishing to be extracted; values: values of variables being extracted in JSON a data structure
    
    hash_ = {
        'Date': [], # Date: The dates the filing is for, in regards to the fiscal period
        
        'Company': [], # Company: Append company name that is being extracted
            
        'AssetsCurrent': [], # AssetsCurrent: Append the values of the variable being extracted
        
        'LiabilitiesCurrent': [], # LiabilitiesCurrent: Append the values of the variable being extracted
        
        'totalInventory': [] # totalInventory: Append the values of the variable being extracted
    }
        
    # list comprehension and cast into tuple IF wanting to use module functools.lru_cache; variable companyArray, contains name of companies
    companyArray = tuple([companies for companies in allFilesExtracted.keys()])
    
    # move through companyArray using index
    companyIndexer = 0
        
    # the json data structure keeps the most recent filings at the end of the files
    index = -1
    # brave checks if the next filing is a duplicate, prevents duplicate extraction
    brave = -2
    
    # False if a new company needs to be extracted
    opened = False
    
    # when data for a company and variable is done being extracted, move to next index for a new variable
    metricIndexer = 0
    
    # metric indexer will move through this tuple of variables  required for a user-defined metric
    metricArray = tuple(['AssetsCurrent', 'LiabilitiesCurrent', 'InventoryNet'])
    
    # False if a new variable needs to be extracted from json data structure
    got_metric = False
    
    # arrayLimit can your desired value; e.g. extract 6 values pertaining to variable, AssetsCurrent
    arrayLimit = 6
    
    # add 1 when a value is extracted
    arraySize = 0
    
    # loop while arraySize is less-than or equal to 5
    while arraySize <= (arrayLimit - 1):
        
        
        if opened == False:
            
            # jsonBranch is allFilesExtracted's value, containing a companies json data structure
            jsonBranch = allFilesExtracted.get(companyArray[companyIndexer])
            
            # opened = True; will prevent opening of jsonBranch while still being parsed
            opened = True
            
            
        if got_metric == False:
        
            # metricTree contains the data to be parsed for a specific variable
            metricTree = jsonBranch[metricArray[metricIndexer]]['units']['USD']
            
            # got_metric = True; will prevent opening of metricTree while still being parsed
            got_metric = True
            
        # extract dates to check if the index and preceding index are duplicates
        date1 = metricTree[index]['end'] 
        date2 = metricTree[brave]['end']
    
        # if dates are not equal, proceed to parse; else, move to next index
        if date1 != date2:
            
            # see metricArray for info on which index contains what variable
            if metricIndexer == 0:
                hash_['AssetsCurrent'].append(metricTree[index]['val']) # val == value
                hash_['Company'].append(companyArray[companyIndexer])
                hash_['Date'].append(metricTree[index]['end']) # end == date
            
            elif metricIndexer == 1:
                hash_['LiabilitiesCurrent'].append(metricTree[index]['val'])
                hash_['Company'].append(companyArray[companyIndexer])
                hash_['Date'].append(metricTree[index]['end']) # end == date
                
            else:
                hash_['totalInventory'].append(metricTree[index]['val'])
                hash_['Company'].append(companyArray[companyIndexer])
                hash_['Date'].append(metricTree[index]['end']) # end == date
            
            # when each value is done being extracted, move to next index and subtract 1 to arraySize until arraySize == arrayLimit
            index -= 1 
            brave -= 1
            arraySize += 1
                
            # if arrayLimit is reached, but not all variables for user-desired metric is extracted, reset variables and move to next variable
            if arraySize == arrayLimit and metricIndexer == 0:
                
                metricIndexer += 1
                arraySize = 0
                index = -1
                brave = -2
                got_metric = False
             
            # if arrayLimit is reached, but not all variables for user-desired metric is extracted, reset variables and move to next variable
            if arraySize == arrayLimit and metricIndexer == 1:
                
                metricIndexer += 1
                arraySize = 0
                index = -1
                brave = -2
                got_metric = False
                
            # if arrayLimit is reached and all variables for user-desired metric is extracted, break loop
            if arraySize == arrayLimit and metricIndexer == 2:
                
                if companyIndexer == (len(companyArray) - 1):
                    break
        # if dates are duplicates, move to next index
        else:
            index -= 1 
            brave -= 1
            
    # convert populated dictionary to a data frame
    df = pd.DataFrame.from_dict(hash_, orient='index').transpose()

    # cast all variable with numeric values into a float
    df[['AssetsCurrent', 'LiabilitiesCurrent', 'totalInventory']] = df[[
        'AssetsCurrent', 'LiabilitiesCurrent', 'totalInventory']].astype(float)
    
    # financial equation for Current Ratio
    df[metric] = round(
        (df.AssetsCurrent - df.totalInventory) / df.LiabilitiesCurrent, 2)
    
    # optional: Change dates to Quarterly format
    df.Date = pd.PeriodIndex(df.Date, freq='Q') # change date format to 
    
    # optional: if graphing, module may require date to be str or date datatype if not converting to Quarterly format
    df.Date = df.Date.astype(str)
        
    # reverse dataframe
    df = df[::-1].reset_index(drop = True)
        
    # return bar graph with populated dataframe
    return plotTemplate(df, metric)
