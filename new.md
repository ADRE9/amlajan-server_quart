# Amlajan Server

## URL: https://quart-app.herokuapp.com
## Endpoints:

[GET]  /getAllProviders
    
    - parameter : None
    - response : returns a list of objects containing all the   
    provider

[GET]  /getProviderById/{<string:pid>}

    -parameter : pid(pass the id of the provider)
    -response  : returns the user object of the specific id


[POST] /{<string:role>}/addUserdetails

    -parameter : pass the "role" of the provider along with the request

    IF "role"=="provider" , then 
    -request : {
        "name":"",
        "contact_number":"",
        "email":"",
        "address":"",
        "incentive":"",
        "lat":    ,
        "long":
    }

    if "role"=="patient",then 

    -request : {
        "name":"",
    }


    -response :  returns the newly created user object

[POST] /checkUserExists/{<string:email>}
    
    -parameter : pass the email of the user
    -response : if exists returns the user object otherwise redirect to the "ROLE" page



[POST] /getNearbyProviders

    -parameter : pass the latitude and longitude of the patient
    
    -request : {
        "lat":  ,
        "long"   
    }

    -response : returns a list of objects




[PUT] /{<string:pid>}/updateProfile

    -parameter : pass the id of the user along with request given below

    -request : {
        "name":"",
        "contact_number":"",
        "email":"",
        "lat":,
        "long":
    }

    -response : returns the updated user object


