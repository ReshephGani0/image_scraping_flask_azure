from flask import Flask, render_template, request, jsonify
from pymongo.mongo_client import MongoClient
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import requests
import logging
logging.basicConfig(filename="image_scrap.log", level=logging.INFO)
from flask_cors import CORS, cross_origin
import os


app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route('/review', methods=['GET','POST'])
def scraping():
    if(request.method=="POST"):
        try:
            search_key = request.form['search_word'].replace(" ","+")

            save_directory = "images/"
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}


            url = f"https://www.google.com/search?q={search_key}&sxsrf=APwXEddsqSwJ3h8-Zc2-rKcpKixgD72z1g:1683858580411&source=lnms&tbm=isch&sa=X&sqi=2&ved=2ahUKEwiW_6WE3u7-AhVHwjgGHRS_DZUQ_AUoAnoECAIQBA&biw=1254&bih=607&dpr=1.09"
            url_response = requests.get(url)

            response_content = url_response.content
            response_html = bs(response_content,"html.parser")

            image_tags = response_html.find_all("img")
            
            #print(len(image_tags))
            del image_tags[0]

            image_data_mongo =[]
            for i in image_tags:
                image_url = i['src']
                image_data = requests.get(image_url).content

                mydict={"index":image_url, "image": image_data}
                image_data_mongo.append(mydict)

                with open(os.path.join(save_directory, f"{search_key}_{image_tags.index(i)}.jpg"), "wb") as f:
                    f.write(image_data)

            uri = "mongodb+srv://pwskills:pwskills1@cluster0.xe9xplu.mongodb.net/?retryWrites=true&w=majority"
            # Create a new client and connect to the server
            client = MongoClient(uri)
            db= client['image_scraping']
            collectn_img = db["collection_image_scraping"]
            collectn_img.insert_many(image_data_mongo)

            return "image loaded"
        except Exception as e:
            logging.info("scraping issue",e)
            return "something is wrong"




        #return  search_key

    else:
        return render_template("index.html")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8000) # now using port 8000 so have to write :8000 on url
