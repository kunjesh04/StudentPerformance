import os
import sys
from dataclasses import dataclass
from src.utils import save_object

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.logger import logging
from src.exception import CustomException

@dataclass
class DataTransformationConfig:
    prepocessor_obj_file_path = os.path.join('artifacts', 'preprocessor.pkl')
    
class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()
        
    def get_data_transformer_obj(self):
        '''
        This function is used for data transformation 
        '''
        try:
            numerical_columns = ['reading_score', 'writing_score']
            categorical_columns = ['gender', 
                                    'race_ethnicity', 
                                    'parental_level_of_education', 
                                    'lunch', 
                                    'test_preparation_course']
            
            num_pipeline = Pipeline(
                steps = [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler(with_mean=False))
                ]
            )
            
            cat_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one hot encoder", OneHotEncoder()),
                    ("scaler", StandardScaler(with_mean=False))
                ]
            )
            
            logging.info("Numerical columns scaling completed")            

            logging.info("Categorical columns encoding completed")
        
            preprocessor = ColumnTransformer(
                [
                    ("numerical pipeline", num_pipeline, numerical_columns),
                    ("categorical pipeline", cat_pipeline, categorical_columns)
                ]
            )
            
            return preprocessor
        
        except Exception as e:
            raise CustomException(e, sys)
        
    def initiate_data_transformation(self, train_path, test_path):
        
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logging.info("Completed Reading of Train and Test data")    
        
            logging.info("Obtaining preprocessing object")
            
            preprocessing_obj = self.get_data_transformer_obj()
            
            target_column_name = 'math_score'
            numerical_columns = ['reading_score', 'writing_score']
            
            input_feature_train_df = train_df.drop(columns=[target_column_name], axis=1)
            target_feature_train_df = train_df[target_column_name]
            
            input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
            target_feature_test_df = test_df[target_column_name]
            
            logging.info("Preprocessing Train and Test Dataframe")
            
            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)
            
            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]
            
            logging.info("Saved Preprocessing Object")
            
            save_object(
                file_path = self.data_transformation_config.prepocessor_obj_file_path,
                obj = preprocessing_obj
            )
            
            return(
                train_arr, 
                test_arr,
                self.data_transformation_config.prepocessor_obj_file_path 
            )
            
        except Exception as e:
            raise CustomException(e, sys)