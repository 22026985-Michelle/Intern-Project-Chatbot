import json
import pandas as pd
from typing import Union, Dict, List, Any
import re
from io import StringIO
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicFormatter:
    def __init__(self):
        # List of supported date formats
        self.date_formats = [
            "%d/%m/%Y",
            "%Y-%m-%d", 
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d %b %Y",
            "%d %B %Y"
        ]

    def detect_format(self, data: str) -> str:
        """
        Detect the input data format.
        
        Args:
            data (str): Input data to detect format for.
        
        Returns:
            str: Detected format ('json', 'tabular', or 'unknown')
        """
        try:
            # Try parsing as JSON first
            json.loads(data.strip())
            return 'json'
        except json.JSONDecodeError:
            # Check for tabular delimiters
            if '\t' in data or ',' in data or '|' in data:
                return 'tabular'
            
            # Check for space-separated multi-column data
            lines = data.strip().split('\n')
            if len(lines) > 1 and all(len(line.split()) > 1 for line in lines[:2]):
                return 'tabular'
        
        return 'unknown'

    def capitalize_keys(self, obj: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
        """
        Recursively capitalize dictionary keys.
        
        Args:
            obj (Union[Dict, List, Any]): Input object to process.
        
        Returns:
            Union[Dict, List, Any]: Object with capitalized keys
        """
        if isinstance(obj, dict):
            return {
                k[0].upper() + k[1:] if isinstance(k, str) else k: 
                self.capitalize_keys(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [self.capitalize_keys(item) for item in obj]
        
        return obj
    
    def format_json(self, data: Union[str, dict], indent: int = 4) -> str:
        """
        Format JSON with proper indentation and capitalized keys.
        
        Args:
            data (Union[str, dict]): Input JSON data.
            indent (int, optional): Indentation level. Defaults to 4.
        
        Returns:
            str: Formatted JSON string
        """
        try:
            # Convert string to dict if needed
            if isinstance(data, str):
                data = json.loads(data)
            
            # Capitalize keys and format
            formatted_data = self.capitalize_keys(data)
            return json.dumps(formatted_data, indent=indent)  # Ensure indentation is applied
            
        except Exception as e:
            logger.error(f"Error formatting JSON: {str(e)}")
            raise

    def format_tabular(self, data: str) -> pd.DataFrame:
        """
        Convert tabular data to a pandas DataFrame.
        
        Args:
            data (str): Input tabular data.
        
        Returns:
            pd.DataFrame: Processed DataFrame
        """
        try:
            # Detect delimiter
            delimiter = '\t' if '\t' in data else ',' if ',' in data else '|'
            
            if delimiter in data:
                # Use pandas CSV reader with detected delimiter
                df = pd.read_csv(StringIO(data), sep=delimiter)
            else:
                # Handle space-separated data
                lines = [re.split(r'\s{2,}', line.strip()) 
                        for line in data.strip().split('\n')]
                df = pd.DataFrame(lines[1:], columns=lines[0])
            
            # Clean column names
            df.columns = self.clean_column_names(df.columns.tolist())
            return df
        
        except Exception as e:
            logger.error(f"Error formatting tabular data: {str(e)}")
            raise

    def clean_column_names(self, columns: List[str]) -> List[str]:
        """
        Clean and format column names.
        
        Args:
            columns (List[str]): List of column names to clean.
        
        Returns:
            List[str]: Cleaned and formatted column names
        """
        cleaned = []
        for col in columns:
            # Remove special characters
            clean_col = re.sub(r'[^\w\s]', ' ', col)
            
            # Remove extra whitespace
            clean_col = ' '.join(clean_col.split())
            
            # Capitalize each word
            clean_col = ' '.join(word.capitalize() for word in clean_col.split())
            
            cleaned.append(clean_col)
        return cleaned

    def df_to_excel_format(self, df: pd.DataFrame) -> str:
        """
        Convert DataFrame to Excel-compatible tab-separated format.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
        
        Returns:
            str: Tab-separated string representation of the DataFrame
        """
        return df.to_csv(sep='\t', index=False)

    def process_data(self, data: str) -> Dict[str, str]:
        """
        Process input data and return both JSON and tabular formats.
        
        Args:
            data (str): Input data to process.
        
        Returns:
            Dict[str, str]: Dictionary with 'json' and 'tabular' formats
        """
        try:
            # Detect input data format
            data_format = self.detect_format(data)
            result = {}

            if data_format == 'json':
                # Process JSON input
                formatted_json = self.format_json(data)
                result['json'] = formatted_json
                
                # Convert to DataFrame
                json_data = json.loads(data)
                df = pd.json_normalize(json_data)
                result['tabular'] = self.df_to_excel_format(df)
            
            elif data_format == 'tabular':
                # Process tabular input
                df = self.format_tabular(data)
                result['tabular'] = self.df_to_excel_format(df)
                result['json'] = self.format_json(df.to_dict(orient='records'))
            
            else:
                raise ValueError("Unrecognized data format")

            return result
        
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise