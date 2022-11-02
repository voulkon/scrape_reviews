import sqlite3
import pandas as pd
import logging

class DbConnector:
    
    def __init__(self,db_name):
        
        self.db_name = db_name #Store as a property in case it's needed
        self.connection = sqlite3.connect(self.db_name )
        logging.info(f"Connected to: {self.db_name}" )
        self.cur = self.connection.cursor()
        self.attempt_to_create_tables()

    def create_entity_info_table(self):

        self.cur.execute("""

        CREATE TABLE IF NOT EXISTS entity_info (
            Name TEXT NOT NULL PRIMARY KEY,
            Overall_Rating TEXT(3),
            Number_of_Ratings TEXT(10),
            'fetched_looking_at_place' TEXT(50),
            fetched_at TEXT(19)
            );
            """
            )

    def create_reviews_table(self):

        self.cur.execute("""

        CREATE TABLE IF NOT EXISTS reviews (
            reviewers_no_of_reviews TEXT(30),
            reviewer TEXT(80),
            rating TEXT(3),
            text_of_review TEXT,
            regards_entity TEXT(80),
            date_created TEXT(30),
            fetched_at TEXT(19),
            'data-review-id' TEXT(36) NOT NULL PRIMARY KEY
            );
            """
            )

    def attempt_to_create_tables(self):
        self.create_entity_info_table()
        self.create_reviews_table()

    def insert_dataframe_in_table(
        self,
        dataframe_to_write_in_db:pd.DataFrame,
        table_name:str
        ):
        dataframe_to_write_in_db.to_sql(name = table_name, con = self.connection, if_exists = 'append',index = False)

    def read_a_table(
        self,
        table_wanted
    ):
        query_to_fetch_it_all = """SELECT * FROM {t}""".format(t = table_wanted)
        self.cur.execute(query_to_fetch_it_all)
        rows = self.cur.fetchall()
        return rows

    def search_reviews(
        self,
        search_keyword
    ):
        keyword_search_query = """ 
        SELECT * 
        FROM reviews 
        WHERE text_of_review LIKE '%{keyword}%'""".format(keyword = search_keyword)

        return self.cur.execute(keyword_search_query).fetchall()
    
    def insert_values_in_table(
        self,
        table_wanted:str,
        items:list        
     ):
        items_part = ",".join(["?" for i,item in enumerate(items)])
        insert_values_query = """
        INSERT OR
        IGNORE INTO
        {table_wanted}
        VALUES({items_part})
        """
        
        insert_values_query_formatted = insert_values_query.format(table_wanted = table_wanted,items_part = items_part )
        
        self.cur.execute(insert_values_query_formatted,items)
        
        self.connection.commit() 
    
    def insert_values_in_table_by_colname(
        self,
        table_wanted:str,
        named_items:dict        
     ):

        columns_part =  ",".join(["'"+ k + "'" for k in named_items.keys()])

        values_part = ",".join([ "'" + v.replace("'", " " ) + "'" for v in named_items.values()])
        
        insert_named_values_query = """
        INSERT OR
        IGNORE INTO
        {table_wanted} ({columns_part})
        VALUES ({values_part})
        """
        
        insert_named_values_query_formatted = insert_named_values_query.format(
            table_wanted = table_wanted,
            values_part = values_part,
            columns_part = columns_part 
            )
        
        self.cur.execute(insert_named_values_query_formatted)
        
        self.connection.commit() 

    def perform_a_query(self,query):
        return self.cur.execute(query).fetchall()
