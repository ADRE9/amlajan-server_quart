import firebase_admin
from firebase_admin import credentials,firestore
import uvicorn
import quart
from quart import abort,jsonify,request,redirect,make_response
from quart_cors import cors
# import uuid
from math import sin, cos, sqrt, atan2, radians
from .schemaValidator import SchemaValidator
import asyncio
# init the quart app
app=quart.Quart(__name__)
#give access to all resources
app = cors(app, allow_origin="*")



#firebase app init
cred = credentials.Certificate("app/secret_key.json")
firebase_app=firebase_admin.initialize_app(cred)
store=firestore.client()


@app.route('/',methods=['GET'])
async def index():
    response={
        "msg":"welcome to homepage"
    }
    return response


@app.route('/<string:role>/addUserdetails',methods=['POST'])
async def addUser(role):
    data= await request.get_json(force=True)
    if role=="provider":
        _instance  = SchemaValidator(response=data)
        response =   _instance.isTrue()
        if len(response) > 0:
            details= {
                    "status":"error",
                    "message":response,
                },403
            return details
        else:
            dict={}
            dict['uid']=data.get("uid")
            dict['displayName']=data.get("displayName")
            dict['contact_number']=data.get("phone")
            dict['email']=data.get("email")
            dict['location']={
                            'lat':data.get("location",None).get("latitude"),
                            'long':data.get("location",None).get("longitude"),
                            'alt':data.get("location",None).get("altitude"),
                            'address':data.get("location",None).get("address"),
                            'accurecy':data.get("location",None).get("accurecy"),
                        }
            dict['role']=role
            dict['rating']=data.get("rating")
            dict['incentive']=data.get("incentive")
            store.collection("Users").document(dict['uid']).set(dict)
            return jsonify({"Response":dict}),201

    else:
        dict={}
        dict['uid']=data.get("uid")
        dict['name']=data.get("displayName")
        dict['role']=role
        store.collection("Users").document(dict['uid']).set(dict)
        return jsonify({"Response":dict}),201


"""check user exists or not"""
"""if exists then return user details"""
"""if not then make a [POST] details"""
@app.route('/checkUserExists',methods=['GET'])
def checkUserExists():
    if request.headers.get('uid'):
        uid = request.headers.get('uid')
        resps=store.collection("Users").where("uid","==",uid).get()
        print(resps)
        if len(resps)!=0:
                for resp in resps:
                    Resp=resp.to_dict()
                return jsonify({"Response":"the User exists","Provider":Resp}),200
        else:
                return jsonify({"Response":"the user does not exists!"}),404
    else:
        return jsonify({"Response":"Send a valid uid"}),400

    
@app.route('/getAllProviders',methods=['GET'])
async def getAllProviders():
    resp=store.collection("Users").where("role","==","provider").stream()
    prvd_lst=list()
    for doc in resp:
        prvd_lst.append(doc.to_dict())
    return jsonify({"Response":200,"Provider_lst":prvd_lst})


"""get provider by id"""
@app.route('/getProviderById',methods=['GET'])
async def getProviderById():
    if request.headers.get('uid'):
        uid = request.headers.get('uid')
        resps= store.collection("Users").where("uid","==",uid).stream()
        for resp in resps:
            Resp=resp.to_dict()
        return jsonify({"Response":200,"Provider":Resp})
    else:
        return jsonify({"Response":"Send a valid uid"}),400        


@app.route('/updateProfile',methods=['PATCH'])
async def updateProfile():
    if request.headers.get('uid'):
        uid = request.headers.get('uid')
        data= await request.get_json(force=True)
        _instance  = SchemaValidator(response=data)
        response = _instance.isTrue()

        if len(response) > 0:
            details= {
                    "status":"error",
                    "message":response,
                },403
            return details
        else:
            try:
                doc_ref=store.collection("Users").document(uid)
                doc_ref.update({
                    "displayName":data.get("displayName"),
                    "contact_number":data.get("phone"),
                    "email":data.get("email"),
                    "location.lat":data.get("location",None).get("latitude"),
                    "location.long":data.get("location",None).get("longitude"),
                    "location.alt":data.get("location",None).get("altitude"),
                    "location.address":data.get("location",None).get("address"),
                    "location.accurecy":data.get("location",None).get("accurecy"),
                    "rating":data.get("rating"),
                    "role":data.get("role"),
                    "incentive":data.get("incentive"),
                })
                resps=store.collection("Users").where("uid","==",uid).stream()
                for resp in resps:
                    Resp=resp.to_dict()
                return jsonify({"Response":Resp}),201

            except Exception as e:
                return f"An Error Occured: {e}",400
    else:
        return jsonify({"Response":"Send a valid uid"}),400



@app.route('/getNearbyProviders',methods=['POST'])
async def getNearbyProvider():
    #radius of Earth
    R=6373.0
    #getting user's cordinate
    data=await request.get_json(force=True)
    myLat=data.get("lat")
    myLong=data.get("long")

    allProvData=store.collection("Users").where("role","==","provider").stream()
    nearByProvData=[]

    for singleProv in allProvData:
        try:
            dit=singleProv.to_dict()

            ## get lat and lang of restaurant
            rLat=dit.get('location').get('lat')
            rLong=dit.get('location').get('long')

            lat1 = radians(rLat)
            lon1 = radians(rLong)
            lat2 = radians(myLat)
            lon2 = radians(myLong)

            dlon=lon2-lon1
            dlat=lat2-lat1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            #dist between user and provider
            distance = R * c
            if distance<=100:
                nearByProvData.append(dit)
                return jsonify({"Response":200,"Prov_list":nearByProvData}),200
                # print(nearByProvData)
            else:
                return jsonify({"Response":"No nearby provider found! \n Sorry 😞"}),404

        except Exception as e:
            return f"An Error Occured: {e}"


@app.route('/deleteProvider',methods=['DELETE'])
def deleteProvider():
    if request.headers.get('uid'):
        uid = request.headers.get('uid')
    del_ref=store.collection(u'Users').document(uid).delete()
    print(del_ref)
    return jsonify({"Response":"User deleted successfully"}),200



if  __name__=='__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info",debug=False)