from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin() # to deploy in cloud platform, this should be given
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString #to land in to the flipkart page with
            # searchstring e.g.,iphone7.
            uClient = uReq(flipkart_url) # searching of iphone7 will perform
            flipkartPage = uClient.read() #extracting all the information in that page
            uClient.close() #close the inforamtion which you read
            flipkart_html = bs(flipkartPage, "html.parser") #using Beautiful soup to make the information as structured one
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})  # trying to filter out the data
            # based on the given class. the class id can be extracted by inspecting the flipkart page with iphone7.
            # div tag will be there, inside that class id will be extracted
            del bigboxes[0:3]
            box = bigboxes[0] # extracting single box details i.e, first iphone7 information
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] # to reach out "href" it has to pass through
            # three div and one a then only it can reach out. You may get product link
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8' # getting the product details in english format
            prod_html = bs(prodRes.text, "html.parser") # using BS extracting the data in beautiful format
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"}) # class id of comments

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text # specifying class id of header comment

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text # getting rating of costumer


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text # extracting comment header

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''}) # specifying class id of comments
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text # Extracting comments
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
