import pandas as pd

def from_info_dict_to_info_df(result_of_scraping:dict[dict[list]]) -> pd.DataFrame:
    
    #import pandas as pd
    
    return pd.DataFrame(result_of_scraping['entity_info'])


def from_reviews_dict_to_reviews_df(result_of_scraping:dict[dict[list]]) -> pd.DataFrame:
    
    #import pandas as pd
    
    to_be_returned = pd.DataFrame({key:[item for sublist in col_to_be for item in sublist] for key,col_to_be in result_of_scraping['reviews'].items()})
    
    return to_be_returned

def to_numeric(column):
    
    return column.str.replace(',','.').astype(float)


def clean_info_df(all_info_df):
    
    all_info_df["Overall_Rating"] = to_numeric(all_info_df["Overall_Rating"])

    all_info_df['Number_of_Ratings'] = all_info_df['Number_of_Ratings'].str.replace("(","").str.replace(")","").astype(int)
    
    return all_info_df


def clean_reviews_df(all_reviews_df):
    
    import pandas as pd

    ##Rating####
    all_reviews_df[['absolute_rating','rating_out_of']] = all_reviews_df['rating'].str.split("/",expand = True).apply(to_numeric)
    all_reviews_df['rating_raw'] = all_reviews_df['rating']
    all_reviews_df['relative_rating'] = (all_reviews_df['absolute_rating'] / all_reviews_df['rating_out_of'])*100
    
    ##Reviews (and removal of new line \n####

    def keep_translated_review(text_of_review, pattern_to_keep = "^\\(.*Google\\) (.*)\\(\\w+ \\w+\\)"):
        
        
        from re import search

        if not isinstance(text_of_review,str):
            return ""

        text_of_review = text_of_review.replace("\n","")

        greek_review_search = search(pattern=pattern_to_keep,  string = text_of_review)
        
        if greek_review_search:
            return greek_review_search.group(1)
        
        return text_of_review
    
    all_reviews_df["text_of_review"] = all_reviews_df["text_of_review"].apply(lambda x: keep_translated_review(x))#.to_csv("REviews_.csv")

    def clean_date_created(text_of_date_created, pattern_for_extraction =  "^(πριν από) ([\S]*) ([\S]*) ?"):
        
        #TODO: create a test with: text_of_date_created = 'πριν από 3 εβδομάδες στο\nGoogle' & text_of_date_created = 'πριν από έναν μήνα'
        #TODO: Make it work with other languages too - now depends on "(πριν από)" --> it should work with "before", "antes", etc.

        contains_new_line = '\n' in text_of_date_created 
        
        if contains_new_line:
            text_of_date_created, listed_at = text_of_date_created.split('\n')
        else:
            listed_at = ""
            
        import re

        search_result = re.search( string =  text_of_date_created,pattern = pattern_for_extraction )
        
        to_be_returned = [search_result.group(2),search_result.group(3),listed_at]

        return to_be_returned

    all_reviews_df[["Created_Before_number","Created_Before_measure_unit_of_time","Review_Listed_at"]] = pd.DataFrame(all_reviews_df["date_created"].apply(lambda x:clean_date_created(x)).tolist())

    
    return all_reviews_df
