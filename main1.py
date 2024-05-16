# library allows you to send HTTP requests easily.
import requests
#it is commonly used for multithreading and multiprocessing tasks.
import concurrent.futures
#This library is used for parsing HTML and XML documents. It provides convenient methods for extracting data from web pages.
from bs4 import BeautifulSoup
#encoding Python data structures into JSON format and decoding JSON data back into Python data structures
import json



class Restaurant:
    #python constructor call it contains parameter exclude self
    def __init__(self, image_link, name, address, rating, time, distance, offer):
        self.image_link = image_link
        self.name = name
        self.address = address
        self.rating = rating
        self.time = time
        self.distance = distance
        self.offer = offer
        
        #it print details of restraunts
    # def __str__(self):
    #     return f"Name: {self.name}\nAddress: {self.address}\nRating: {self.rating}\nTime: {self.time}\nDistance: {self.distance}\nOffer: {self.offer}\n\n\n"
    def to_dict(self):
        return {
            "image_link": self.image_link,'\n'
            "name": self.name,'\n'
            "address": self.address,'\n'
            "rating": self.rating,'\n'
            "time": self.time,'\n'
            "distance": self.distance,'\n'
            "offer": self.offer
        }

def food_scrape_restro(url, location):
    """
    The User-Agent header in an HTTP request allows the client
    to identify itself to the server. By specifying a User-Agent header, 
    you can inform the server about the client making the request. 
    This is particularly useful for web scraping, as some websites may 
    behave differently based on the user agent.
    """
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    headers = {'User-Agent': user_agent}
    
    # Modify the URL to include the location-specific parameters
    url += f'?location={location}'

    try:
        #
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        #it convert it intohtml content
        html_text = response.content

        soup = BeautifulSoup(html_text, 'html.parser')
        
        restaurant_details = []
    
        # details of all restraunts
        restaurants =  soup.find_all('div', class_='ant-row-flex ant-row-flex-start ant-row-flex-top')

        for restaurant_element in restaurants:
            details = restaurant_element.find('div', class_='ant-col-24 colInfo___3iLqj ant-col-md-24 ant-col-lg-24')

            
            image = soup.find('img')
            #image link of image
            image_link = image.get('src')  if image else None

            names = details.get_text()
            name = names.split(",")
            #restro name 
            restro_name = name[0]
            
            #address of restraunt
            address = details.find('div', class_='basicInfoRow___UZM8d cuisine___T2tCh').get_text()

            #rating of restraunt
            rating = details.find('div', class_='numbersChild___2qKMV').get_text()

            rating_time_and_distance = details.find('div', class_='basicInfoRow___UZM8d numbers___2xZGn').get_text()
            time_and_distance = rating_time_and_distance.replace(rating, "", 1)
            delimiter = '•'

            #time and distance of restraunt
            time, distance = time_and_distance.split(delimiter)

            offer = details.find('div', class_='basicInfoRow___UZM8d discount___3h-0m')
            #offer exist or not
            offer_exist = offer.get_text() if offer is not None else "Sorry! No Offer"
            
            #putting all things into class restraunt and then append into restaurant_details array
            restaurant = Restaurant(image_link, restro_name, address, rating, time.strip(), distance.strip(), offer_exist)
            restaurant_details.append(restaurant)

            return restaurant_details
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Main function
def main():
    #location_choices is a dictionary that use key value pair. if user select key based on that key it gives value(location)
    location_choices = {
        "1": "PT Singapore - Choa Chu Kang North 6, Singapore, 689577",
        "2": "Chong Boon Dental Surgery - Block 456 Ang Mo Kio Avenue 10, #01-1574, Singapore, 560456"
    }
     
     #print normally what user choose location
    print("Select a location to scrape the list of restaurants and their details:")
    for key, value in location_choices.items():
        print(f"{key}. {value}")

    choice = input("Enter your choice (1 or 2): ")
    
    #it will give location based on choice of user
    selected_location = location_choices.get(choice)

    if selected_location:
        # url of food scrap website
        url = 'https://food.grab.com/sg/en/' 
        urls = [url] * 5  # Example: Repeat the same URL 5 times for demonstration purposes
        with concurrent.futures.ThreadPoolExecutor() as executor:
             # Submit scraping tasks to the executor
            future_to_url = {executor.submit(food_scrape_restro, url, selected_location): url for url in urls}
              # Process results as they become available

            restaurant_data = []
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    restaurants = future.result()
                    for restaurant in restaurants:
                        restaurant_data.append(restaurant.to_dict())
                except Exception as e:
                    print(f"Error scraping {url}: {e}")

                    # Write data to file in NDJSON format
            with open('restaurant_data.ndjson', 'w') as file:
                for restaurant in restaurant_data:
                    json.dump(restaurant, file)
                    file.write('\n')
    else:
        print("Invalid choice. Please select a valid location.")

if __name__ == "__main__":
    #calling main function
    main()
