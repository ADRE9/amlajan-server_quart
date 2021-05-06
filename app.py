import firebase_admin
from firebase_admin import credentials,firestore
  
import uvicorn
import quart
from quart import abort,jsonify,request,redirect
import asyncio

# init the flask app
app=quart.Quart(__name__)


#firebase app init
cred = credentials.Certificate("secret_key.json")
firebase_app=firebase_admin.initialize_app(cred)
store=firestore.client()


@app.route('/addUserdetails',methods=['POST'])
async def addUser():
    data= await request.get_json(force=True)
    dict={}
    dict['name']=  data.get("name")
    dict['contact_number']=  data.get("contact_number")
    dict['email']= data.get("email")
    dict['address']= data.get("address")
    dict['role']= data.get("role")
    dict['review']= data.get("review")
    dict['incentive']= data.get("incentive")
    dict["createdAt"]=firestore.SERVER_TIMESTAMP

    resp=store.collection("Users").document(dict['name']).set(dict)
    print(resp)
    return jsonify({"Response":200})




@app.route('/getAllProviders',methods=['GET'])
async def getAllProviders():
    await asyncio.sleep(2)
    resp=store.collection("Users").where("role","==","provider").stream()
    prvd_lst=list()
    for doc in resp:
        prvd_lst.append(doc.to_dict())
    return jsonify({"Response":200,"Provider_lst":prvd_lst})





# @app.route('/updateProfile',methods=['POST'])
# async def updateProfile():
#     data= await request.get_json(force=True)






if  __name__=='__main__':
    # app.run(host='0.0.0.0',port=5000,debug=False)
    uvicorn.run("app:app", host="127.0.0.1", port=5000, log_level="info")