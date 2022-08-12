from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://suhail:123@cluster0.fxu8lrw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Attendance"]
students = db["student"]
attendenceInfo = db["attendanceInfo"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    student = students.find_one({"number": number})
    if bool(student) == False:
        res.message("Hi, thanks for contact *Attendance Bot*.\n\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣  To *contact* us \n 2️⃣  To *attendance* Info \n 3️⃣  To know our *service "
                    "hours* \n "
                    "4️⃣  SEUSL *Library Address* \n"
                    "5⃣  Quit")
        students.insert_one({"number": number, "status": "main", "messages": []})

    elif student["status"] == "main":
        # res.message("I do not know what to say")
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message("You can contact us through phone or email. "
                        "\n\n*phone*: +94 67 2052801 \n*E-mail*:"
                        "ft@seu.ac.lk")
        elif option == 2:
            res.message("*You have entered Attendance Info mode*")
            students.update_one({"number": number}, {"$set": {"status": "attendenceInfo"}})
            res.message("You can select one of the "
                        "following Attendance Information: "
                        "\n\n1️⃣ Monthly Attendance  \n2️⃣ Semester Attendance "
                        "\n3️⃣ Day Attendance\n0️⃣ Go Back")
        elif option == 3:
            res.message("Our service every weekdays *8.00 AM to 5.00 PM*")
        elif option == 4:
            res.message("Library Email: *https://www.seu.ac.lk/library/*")
        elif option == 5:
            res.message("*Thanks for contact us. Have a Great Day*")
            students.update_one({"number": number}, {"$set": {"status": "main"}})
        else:
            res.message("Please Enter a valid response")
            return str(res)

        ## Attendance Page

    elif student["status"] == "attendenceInfo":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            students.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣  To *contact* us "
                        "\n 2️⃣  To *attendance* Info "
                        "\n 3️⃣  To know our *service hours* \n"
                        " 4️⃣  SEUSL *Library Address*"
                        "\n 5⃣  Quit")

        elif 1 <= option <= 3:
            # AttInfo = ["Monthly Attendance", "Semester Attendance",
            #            "Day Attendance"]
            # selected = AttInfo[option - 1]

            students.update_one(
                {"number": number}, {"$set": {"status": "address"}})
            # students.update_one(
            #     {"number": number}, {"$set": {"Info": selected}})
            res.message("We will verify your request and let you know")
            res.message("Please Enter Your Registration Number ")
        else:
            res.message("Please Enter a valid response")
            return str(res)

    elif student["status"] == "address":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        a = attendenceInfo.find_one({'regNo': 110})
        month = a['monthlyAttendance']
        day = a['dayAttendance']
        semester = a['semesterAttendance']

        if option == 1:
            res.message(f"*Monthly attendance* : {month}")
        elif option == 2:
            res.message(f"*Semester attendance* : {semester}")
        elif option == 3:
            res.message(f"*Day attendance* : {day}")
        elif option == 0:
            res.message("*You have entered Attendance Info mode*")
            students.update_one({"number": number}, {"$set": {"status": "attendenceInfo"}})
            res.message("You can select one of the "
                        "following Attendance Information: "
                        "\n\n1️⃣ Monthly Attendance  \n2️⃣ Semester Attendance "
                        "\n3️⃣ Day Attendance\n0️⃣ Go Back")
        else:
            res.message("Your reg number is verified, now please choose the attendance mode")

    students.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()
