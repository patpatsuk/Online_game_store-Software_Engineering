import unittest
import search
from unittest.mock import patch
# from .search import get_unique_game_genres, get_unique_creator_names, get_price_ranges

class TestSearchFunctions(unittest.TestCase):

     #test for genre with 1 match and 1 not match test case
    @patch('search.es.search')
    def test_get_unique_game_genres_match(self, mock_search):
        # Mock Elasticsearch response
        mock_search.return_value = {'hits': {'hits': [{'_source': {'Genre': 'Action'}}]}}

        # Call the function
        result = search.get_unique_game_genres()

     # Verify the result
        expected_result = ['Action']
        if result == expected_result:
            print(f"\nGenre test1 :matches \nActual output: {result} , Expected output: {expected_result}")
        else:
            print(f"\nGenre test1 :not matches \nActual output: {result} , Expected output: {expected_result}")

    @patch('search.es.search')
    def test_get_unique_game_genres_no_match(self, mock_search):
        # Mock Elasticsearch response
        mock_search.return_value = {'hits': {'hits': [{'_source': {'Genre': 'Adventure'}}]}}

        # Call the function
        result = search.get_unique_game_genres()

        # Verify the result
        expected_result = ['Action']
        if result == expected_result:
                print(f"\nGenre test2 :matches \nActual output: {result} , Expected output: {expected_result}")
        else:
            print(f"\nGenre test2 :not matches \nActual output: {result} , Expected output: {expected_result}")
        
    #test for price with 1 match and 1 not match test case
    @patch('search.get_unique_game_genres')
    @patch('search.get_unique_creator_names')
    @patch('search.es.search')
    def test_get_price_ranges_match(self, mock_search, mock_get_unique_creator_names, mock_get_unique_game_genres):
        # Mock Elasticsearch response
        mock_search.return_value = {'aggregations': {'max_price': {'value': 200}}}
        mock_get_unique_game_genres.return_value = ['Genre1', 'Genre2']
        mock_get_unique_creator_names.return_value = ['Creator1', 'Creator2']

        # Call the function
        result = search.get_price_ranges()

        # Verify the result
        expected_result = ["< 100 Baht", "100-150 Baht", "150-200 Baht", "200-250 Baht"]
        if result == expected_result:
            print(f"\nPrice test1 :Output matches, \nActual output: {result} ,\nExpected output: {expected_result}")
        else:
            print(f"\nPrice test1 :Output does not match, \nActual output: {result} ,\nExpected output: {expected_result}")

    @patch('search.get_unique_game_genres')
    @patch('search.get_unique_creator_names')
    @patch('search.es.search')
    def test_get_price_ranges_no_match(self, mock_search, mock_get_unique_creator_names, mock_get_unique_game_genres):
        # Mock Elasticsearch response
        mock_search.return_value = {'aggregations': {'max_price': {'value': 300}}}
        mock_get_unique_game_genres.return_value = ['Genre1', 'Genre2']
        mock_get_unique_creator_names.return_value = ['Creator1', 'Creator2']

        # Call the function
        result = search.get_price_ranges()

        # Verify the result
        expected_result = ["< 100 Baht", "100-150 Baht", "150-200 Baht", "200-250 Baht"]
        if result != expected_result:
            print(f"\nPrice test2 :Output does not match, \nActual output: {result} ,\nExpected output: {expected_result}")
        else:
            print(f"\nPrice test2 :Output matches, \nActual output: {result} ,\nExpected output: {expected_result}")

    
    #test for creator with 1 match and 1 not match test case
    @patch('search.es.search')
    def test_get_unique_creator_names_match(self, mock_search):
        # Mock Elasticsearch response
        mock_search.return_value = {'hits': {'hits': [{'_source': {'Creator': 'John Doe'}}]}}

        # Call the function
        result = search.get_unique_creator_names()

        # Verify the result
        expected_result = ['John Doe']
        if result == expected_result:
            print(f"\nCreator test1 :matches \nActual output: {result} , Expected output: {expected_result}")
        else:
            print(f"\nCreator test1 :not matches \nExpected output: {expected_result}, Actual output: {result}")

    @patch('search.es.search')
    def test_get_unique_creator_names_no_match(self, mock_search):
        # Mock Elasticsearch response
        mock_search.return_value = {'hits': {'hits': [{'_source': {'Creator': 'Jane Doe'}}]}}

        # Call the function
        result = search.get_unique_creator_names()

        # Verify the result
        expected_result = ['John Doe']
        if result == expected_result:
            print(f"\nCreator test2 :matches \nActual output: {result} , Expected output: {expected_result}")
        else:
            print(f"\nCreator test2 :not matches \nActual output: {result} , Expected output: {expected_result}")

if __name__ == '__main__':
    unittest.main()
