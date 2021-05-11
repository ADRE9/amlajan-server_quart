import firebase_admin
from firebase_admin import credentials,firestore
import uvicorn
import quart
from quart import abort,jsonify,request,redirect,make_response
import uuid
from math import sin, cos, sqrt, atan2, radians
from schemaValidator import SchemaValidator
import asyncio

# init the quart app
app=quart.Quart(__name__)



#firebase app init
cred = credentials.Certificate("secret_key.json")
firebase_app=firebase_admin.initialize_app(cred)
store=firestore.client()


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
            dict['id']=str(uuid.uuid4().fields[-1])[:5]
            dict['name']=data.get("name")
            dict['contact_number']=data.get("contact_number")
            dict['email']=data.get("email")
            dict['address']=data.get("address")
            dict['location']={
                            'lat':data.get("lat"),
                            'long':data.get("long")
                        }
            dict['role']=role
            dict['review']=data.get("review")
            dict['incentive']=data.get("incentive")
            store.collection("Users").document(dict['name']).set(dict)
            return jsonify({"Response":dict}),201

    else:
        dict={}
        dict['id']=str(uuid.uuid4().fields[-1])[:5]
        dict['name']=data.get("name")
        dict['role']=role
        store.collection("Users").document(dict['name']).set(dict)
        return jsonify({"Response":dict}),201


"""check user exists or not"""
"""if exists then return user details"""
"""if not then make a [POST] details"""
@app.route('/checkUserExists/<string:email>',methods=['POST'])
def checkUserExists(email):
    resps=store.collection("Users").where("email","==",email).get()
    if len(resps)!=0:
        for resp in resps:
            Resp=resp.to_dict()
        return jsonify({"Response":"the User exists","Provider":Resp}),200
    else:
        return jsonify({"Response":"the user does not exists!"})


@app.route('/getAllProviders',methods=['GET'])
async def getAllProviders():
    await asyncio.sleep(2)
    resp=store.collection("Users").where("role","==","provider").stream()
    prvd_lst=list()
    for doc in resp:
        prvd_lst.append(doc.to_dict())
    return jsonify({"Response":200,"Provider_lst":prvd_lst})


"""get provider by id"""
@app.route('/getProviderById/<string:pid>',methods=['GET'])
async def getProviderById(pid):
    await asyncio.sleep(2)
    resps=store.collection("Users").where("id","==",pid).stream()
    for resp in resps:
        Resp=resp.to_dict()
    return jsonify({"Response":200,"Provider":Resp})
    

@app.route('/<string:pid>/updateProfile',methods=['PUT'])
async def updateProfile(pid):
    data= await request.get_json(force=True)
    _instance  = SchemaValidator(response=data)
    response = await _instance.isTrue()

    if len(response) > 0:
        details= {
                "status":"error",
                "message":response,
            },403
        return details
    else:
        try:
            doc_ref=store.collection("Users").document(data.get("name"))
            doc_ref.update({
                "name":data.get("name"),
                "contact_number":data.get("contact_number"),
                "email":data.get("email"),
                "location.lat":data.get("lat"),
                "location.long":data.get("long")
            })
            resps=store.collection("Users").where("id","==",pid).stream()
            for resp in resps:
                Resp=resp.to_dict()
            return jsonify({"Response":Resp}),201

        except Exception as e:
            return f"An Error Occured: {e}"


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
                return jsonify({"Response":200,"Prov_list":nearByProvData})
                # print(nearByProvData)
            else:
                return jsonify({"Response":"No nearby provider found! \n Sorry 😞"}),404

        except Exception as e:
            return f"An Error Occured: {e}"

    












if  __name__=='__main__':
    # app.run(host='0.0.0.0',port=5000,debug=False)
    uvicorn.run("app:app", host="127.0.0.1", port=5000, log_level="info",debug=False)