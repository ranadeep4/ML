import sys 
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer # used to create the pipeline
from sklearn.impute import SimpleImputer # to handle missing values
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder , StandardScaler
from src.exception import CustomException 
from src.logger import logging 
import os
from src.utils import save_object


@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts','preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_tranformation_config = DataTransformationConfig()  
    def get_data_transformer_obj(self):
        
        """
        this function is responsible for data transformation based on the different types of data
        """
        
        try:
            numerical_columns = ["writing_score","reading_score"]
            categorical_columns = [
                "gender","race_ethnicity","parental_level_of_education", "lunch","test_preparation_course"
            ]
            num_pipeline = Pipeline(
                steps=[
                    ("imputer",SimpleImputer(strategy = "median")),
                    ("scaler",StandardScaler())
                ]   
            )
            
            logging.info(f"Numerical columns : {numerical_columns}")
            
            cat_pipeline = Pipeline(
                steps=[
                    ('imputer',SimpleImputer(strategy = "most_frequent")),
                    ("one_hot_encoder",OneHotEncoder()),
                    ("scaler",StandardScaler(with_mean=False))
                ]
            )
            
            
            logging.info(f"Categorical columns : {categorical_columns}")
            
            
            preprocessor = ColumnTransformer(
                [
                    ("num_pipeline",num_pipeline,numerical_columns),
                    ("cat_pipeline",cat_pipeline,categorical_columns)
                ]
            )
            
            return preprocessor
        
        except Exception as e:
            raise CustomException(e,sys)
    def initiate_data_transformation(self,train_path,test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logging.info("read train and test data completed")
            
            logging.info("obtaining preprocessing object")
            preprocessing_obj = self.get_data_transformer_obj()
            target_column_name = 'math_score'
            numerical_columns = ["writing_score","reading_score"]
            # categorical_columns = [
            #     "gender","race_ethnicity","parantal_level_of_education", "lunch","test_preparation_course"
            # ]
            
            input_feature_train_df = train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df = train_df[target_column_name]
            
            input_feature_test_df = test_df.drop(columns=[target_column_name],axis = 1)
            target_feature_test_df = test_df[target_column_name]
            
            logging.info(
                f"applying preprocessing object on training dataframe and testing dataframe."
            )
            
            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)
            train_arr = np.c_[input_feature_train_arr,np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr,np.array(target_feature_test_df)]
            logging.info(f"saved preprocessing object.")
            
            # utils function
            save_object(
                file_path = self.data_tranformation_config.preprocessor_obj_file_path,
                obj = preprocessing_obj
            )
            
            return (
                train_arr,
                test_arr,
                self.data_tranformation_config.preprocessor_obj_file_path
            )
        except Exception as e:
            raise CustomException(e,sys)