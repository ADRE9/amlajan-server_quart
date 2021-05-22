import firebase_admin
from firebase_admin import credentials, firestore
import uvicorn
import quart
from quart import abort, jsonify, request, redirect, make_response
from quart_cors import cors

# import uuid
from math import sin, cos, sqrt, atan2, radians
from schemaValidator import SchemaValidator
import asyncio

# init the quart app
app = quart.Quart(__name__)
# give access to all resources
app = cors(app, allow_origin="*")


# firebase app init
cred = credentials.Certificate("secret_key.json")
firebase_app = firebase_admin.initialize_app(cred)
store = firestore.client()


@app.route("/", methods=["GET"])
async def index():
    response = {"msg": "welcome to homepage"}
    return response


@app.route("/<string:role>/addUserdetails", methods=["POST"])
async def addUser(role):
    data = await request.get_json(force=True)
    if role == "provider":
        _instance = SchemaValidator(response=data)
        response = _instance.isTrue()
        if len(response) > 0:
            details = {
                "status": "error",
                "message": response,
            }, 403
            return details
        else:
            dict = {}
            dict["uid"] = data.get("uid")
            dict["displayName"] = data.get("displayName")
            dict["contact_number"] = data.get("phoneNumber")
            dict["email"] = data.get("email")
            dict["location"] = {
                "latitude": data.get("location", None).get("latitude"),
                "longitude": data.get("location", None).get("longitude"),
                "altitude": data.get("location", None).get("altitude"),
                "address": data.get("location", None).get("address"),
                "accuracy": data.get("location", None).get("accuracy"),
            }
            dict["role"] = role
            dict["photoURL"] = data.get("photoURL")
            dict["rating"] = data.get("rating")
            dict["incentive"] = data.get("incentive")
            store.collection("Users").document(dict["uid"]).set(dict)
            return jsonify({"Response": dict}), 201

    else:
        dict = {}
        dict["uid"] = data.get("uid")
        dict["name"] = data.get("displayName")
        dict["role"] = role
        store.collection("Users").document(dict["uid"]).set(dict)
        return jsonify({"Response": dict}), 201


"""check user exists or not"""
"""if exists then return user details"""
"""if not then make a [POST] details"""


@app.route("/checkUserExists", methods=["GET"])
def checkUserExists():
    if request.headers.get("uid"):
        uid = request.headers.get("uid")
        prov_ref = store.collection("Users").document(uid)
        prov = prov_ref.get()
        prov = prov.to_dict()
        if prov:
            return jsonify({"Response": "the User exists", "Provider": prov}), 200
        else:
            return jsonify({"Response": "the user does not exists!"}), 404
    else:
        return jsonify({"Response": "Send a valid uid"}), 400


@app.route("/getAllProviders", methods=["GET"])
async def getAllProviders():
    resp = store.collection("Users").where("role", "==", "provider").stream()
    prvd_lst = list()
    for doc in resp:
        prvd_lst.append(doc.to_dict())
    return jsonify({"Response": 200, "Provider_list": prvd_lst})


@app.route("/getProviderById", methods=["GET"])
async def getProviderById():
    if request.headers.get("uid"):
        uid = request.headers.get("uid")
        prov_ref = store.collection("Users").document(uid)
        prov = prov_ref.get()
        prov = prov.to_dict()
        if prov:
            return jsonify({"Response": 200, "Provider": prov})
        else:
            return jsonify({"Response": "the provider does not exists"}), 404
    else:
        return jsonify({"Response": "Send a valid uid"}), 400


@app.route("/updateProfile", methods=["PATCH"])
async def updateProfile():
    if request.headers.get("uid"):
        uid = request.headers.get("uid")
        data = await request.get_json(force=True)
        _instance = SchemaValidator(response=data)
        response = _instance.isTrue()

        if len(response) > 0:
            details = {
                "status": "error",
                "message": response,
            }, 403
            return details
        else:
            try:
                doc_ref = store.collection("Users").document(uid)
                doc_ref.update(
                    {
                        "displayName": data.get("displayName"),
                        "contact_number": data.get("phoneNumber"),
                        "email": data.get("email"),
                        "location.latitude": data.get("location", None).get("latitude"),
                        "location.longitude": data.get("location", None).get("longitude"),
                        "location.altitude": data.get("location", None).get("altitude"),
                        "location.address": data.get("location", None).get("address"),
                        "location.accuracy": data.get("location", None).get("accuracy"),
                        "rating": data.get("rating"),
                        "photoURL": data.get("photoURL"),
                        "role": data.get("role"),
                        "incentive": data.get("incentive"),
                    }
                )
                resp = store.collection("Users").document(uid).get()
                Resp = resp.to_dict()
                if Resp:
                    return jsonify({"Provider": Resp}), 201
            except Exception as e:
                return f"An Error Occured: {e}", 400
    else:
        return jsonify({"Response": "Send a valid uid"}), 400


@app.route("/getNearbyProviders", methods=["POST"])
async def getNearbyProvider():
    # radius of Earth
    R = 6373.0
    # getting user's cordinate
    data = await request.get_json(force=True)
    myLat = data.get("latitude")
    myLong = data.get("longitude")

    allProvData = store.collection("Users").where("role", "==", "provider").stream()
    nearByProvData = []
    for singleProv in allProvData:
        try:
            dit = singleProv.to_dict()
            ## get lat and lang of provider
            rLat = dit.get("location").get("latitude")
            rLong = dit.get("location").get("longitude")

            lat1 = radians(rLat)
            lon1 = radians(rLong)
            lat2 = radians(myLat)
            lon2 = radians(myLong)

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            # dist between user and provider
            distance = R * c
            print(distance)
            if distance <= 100:
                dit["distance"] = distance
                nearByProvData.append(dit)
                continue
        except Exception as e:
            return f"An Error Occured: {e}"

    if len(nearByProvData) != 0:
        return jsonify({"Response": 200, "Provider_list": nearByProvData}), 200
    else:
        return jsonify({"Response": "No nearby provider found! \n Sorry 😞"}), 404


@app.route("/deleteProvider", methods=["DELETE"])
async def deleteProvider():
    if request.headers.get("uid"):
        uid = request.headers.get("uid")
        del_ref = store.collection("Users").document(uid).delete()
        return jsonify({"Response": "User deleted successfully"}), 200
    else:
        return jsonify({"Response": "Send a valid uid"}), 400


# @app.route('/upload',methods=['POST'])
# def pic_upload():
#     file = request.files['file']

"""Admin purpose only"""


@app.route("/admin/getAllUsers", methods=["GET"])
async def getAllUsers():
    users_ref = store.collection("Users")
    docs = users_ref.stream()
    usr_lst = list()
    for doc in docs:
        usr_lst.append(doc.to_dict())
    return jsonify({"Users": usr_lst}), 200


@app.route("/admin/addProvider", methods=["POST"])
async def addProvider():
    data = await request.get_json(force=True)
    _instance = SchemaValidator(response=data)
    response = _instance.isTrue()
    if len(response) > 0:
        details = {
            "status": "error",
            "message": response,
        }, 403
        return details
    else:
        dict = {}
        dict["uid"] = data.get("uid")
        dict["displayName"] = data.get("displayName")
        dict["contact_number"] = data.get("phoneNumber")
        dict["email"] = data.get("email")
        dict["location"] = {
            "latitude": data.get("location", None).get("latitude"),
            "longitude": data.get("location", None).get("longitude"),
            "altitude": data.get("location", None).get("altitude"),
            "address": data.get("location", None).get("address"),
            "accuracy": data.get("location", None).get("accuracy"),
        }
        dict["role"] = "provider"
        dict["photoURL"] = data.get("photoURL")
        dict["rating"] = data.get("rating")
        dict["incentive"] = data.get("incentive")
        store.collection("Users").document(dict["uid"]).set(dict)
        return jsonify({"Provider": dict}), 201


@app.route("/admin/editprovider", methods=["PATCH"])
async def editProvider():
    if request.headers.get("uid"):
        uid = request.headers.get("uid")
        data = await request.get_json(force=True)
        _instance = SchemaValidator(response=data)
        response = _instance.isTrue()

        if len(response) > 0:
            details = {
                "status": "error",
                "message": response,
            }, 403
            return details
        else:
            try:
                doc_ref = store.collection("Users").document(uid)
                doc_ref.update(
                    {
                        "displayName": data.get("displayName"),
                        "contact_number": data.get("phoneNumber"),
                        "email": data.get("email"),
                        "location.latitude": data.get("location", None).get("latitude"),
                        "location.longitude": data.get("location", None).get("longitude"),
                        "location.altitude": data.get("location", None).get("altitude"),
                        "location.address": data.get("location", None).get("address"),
                        "location.accuracy": data.get("location", None).get("accuracy"),
                        "rating": data.get("rating"),
                        "photoURL": data.get("photoURL"),
                        "role": data.get("role"),
                        "incentive": data.get("incentive"),
                    }
                )
                resps = store.collection("Users").where("uid", "==", uid).stream()
                for resp in resps:
                    Resp = resp.to_dict()
                return jsonify({"Provider": Resp}), 201

            except Exception as e:
                return f"An Error Occured: {e}", 400
    else:
        return jsonify({"Response": "Send a valid uid"}), 400


@app.route("/admin/deleteProvider", methods=["DELETE"])
async def adminDeleteProvider():
    if request.headers.get("uid"):
        uid = request.headers.get("uid")
        del_ref = store.collection("Users").document(uid).delete()
        return jsonify({"Response": "User deleted successfully"}), 200
    else:
        return jsonify({"Response": "Send a valid uid"}), 400


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info", debug=True)
