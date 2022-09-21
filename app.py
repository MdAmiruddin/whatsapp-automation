from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://whatsapp:whatsapp@cluster0.7ubyvr9.mongodb.net/?retryWrites=true&w=majority")
db = cluster["database"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")[:-2]
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        msg = res.message("Hi, thanks for contacting *Cyber Intelligence solutions*.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *know* services we provide to our customers \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        msg.media("https://cyberintelligencesolution.com/images/slide.jpg")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message(
                "You can contact us through phone or e-mail.\n\n*Phone*: 92345##### \n*E-mail* : cyberintelligencesolutions115@gmail.com")
        elif option == 2:
            res.message("You have entered *Services*.")
            users.update_one(
                {"number": number}, {"$set": {"status": "ordering"}})
            res.message(
                "You can select one of the following sevices to book an appointment: \n\n1️⃣ Managed Services  \n2️⃣ Security Consulting \n3️⃣ Training Programs"
                "\n4️⃣  eCommerce Solutions \n5️⃣ Cyber Security \n6️⃣ Placements \n0️⃣ Go Back")
        elif option == 3:
            res.message("We work 24/7 monitoring threat analysis to keep your business protected.")

        elif option == 4:
            res.message(
                "Unit No. 115, Cyber Intelligence Solutions, Block EP & GP, Sector V, Salt Lake City, Godrej Genesis Building, 11th Floor ZIOKS Workspace, Kolkata, West Bengal 700091")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address*")
        elif 1 <= option <= 6:
            services = ["Managed Services", "Security Consulting", "Training Programs", "eCommerce Solutions", "Cyber Security", "Placements"]
            selected = services[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "address"}})
            users.update_one(
                {"number": number}, {"$set": {"item": selected}})
            res.message("Excellent choice 😉")
            res.message("Please enter your Name & Address to confirm the appointment")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thankyou for contacting *Cyber Intelligencence Solutions* 😊")
        res.message(f"Your appointment for *{selected}* has been received and we will contact you soon")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one(
            {"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *know* services we provide to our customers \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()
